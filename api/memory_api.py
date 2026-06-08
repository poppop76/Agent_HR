"""
记忆管理 API 路由
"""
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from schemas.ai_schema import ChatHistoryRequest, SessionListRequest, SessionSwitchRequest, ChatQueryRequest
from fastapi.responses import StreamingResponse
import json
import uuid
from core.redis_client import redis_client
from agent.memory.memory_manager import MemoryManager
from agent.monitoring.metrics_collector import get_metrics_collector

router = APIRouter(prefix=settings.API_PREFIX)

# 初始化记忆管理器
memory_manager = MemoryManager(redis_client)


@router.post("/ai/chat-with-memory")
def chat_with_memory(req: ChatQueryRequest,
                     db: Session = Depends(get_db)):
    """对话式查询（流式输出，带记忆功能）"""
    from agent.react_agent import ReactAgent
    import time

    # 生成或使用现有会话 ID
    session_id = req.context.get("session_id") if req.context else None
    if not session_id:
        session_id = str(uuid.uuid4())
    
    user_id = req.context.get("user_id") if req.context else None
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        print(f"[对话] 收到查询：{req.question[:50]}..., session={session_id}", flush=True)
        
        # 1. Query改写 - 将用户问题改写成更精准的查询
        session_context = {
            'session_id': session_id,
            'user_id': user_id
        }
        rewritten_query = memory_manager.rewrite_query(req.question, session_context)
        
        # 如果改写结果与原始问题不同，记录日志
        if rewritten_query != req.question:
            print(f"[对话] Query改写: '{req.question}' -> '{rewritten_query}'", flush=True)
        
        # 2. 使用改写后的查询搜索相关记忆
        memory_results = memory_manager.search_memory(session_id, rewritten_query, use_long_term=True)
        
        # 3. 获取上下文
        llm_context = memory_manager.get_context_for_llm(session_id)
        
        # 4. 如果有相关记忆，添加到提示词中
        system_prompt = None
        if memory_results:
            memory_text = "\n".join([f"- {r['content']}" for r in memory_results[:3]])
            system_prompt = f"""你是一个专业的 HR 助手。
以下是之前对话的相关记忆，请参考这些信息回答问题：
{memory_text}

注意：如果用户问题与记忆相关，请结合记忆内容回答；如果无关，正常回答即可。"""
            print(f"[对话] 加载了 {len(memory_results)} 条相关记忆", flush=True)
        
        agent = ReactAgent()

        def generate():
            print("[对话] 开始流式生成...", flush=True)
            count = 0
            full_response = ""
            
            # 使用改写后的查询进行检索，但使用原始问题进行回答
            for chunk in agent.execute_stream(query=req.question, system_prompt=system_prompt):
                count += 1
                full_response += chunk
                print(f"[对话] 输出第{count}块", flush=True)
                yield chunk
            
            print(f"[对话] 流式生成结束，共{count}块", flush=True)
            
            # 5. 异步保存对话到记忆系统
            memory_manager.add_message(session_id, "user", req.question, user_id=user_id)
            memory_manager.add_message(session_id, "assistant", full_response, user_id=user_id)
            
            # 6. 收集监控指标
            try:
                # 计算响应时间
                response_time = time.time() - start_time
                
                # 估算Token使用量（简化计算）
                input_tokens = len(req.question.split()) + len(str(llm_context).split())
                output_tokens = len(full_response.split())
                cached_tokens = len(rewritten_query.split()) if rewritten_query != req.question else 0
                total_tokens = input_tokens + output_tokens
                
                # 准备检索数据
                retrieval_data = {
                    'retrieved_docs': memory_results,
                    'relevant_docs': memory_results[:3]  # 假设前3个是相关的
                }
                
                # 准备Token数据
                token_data = {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'cached_tokens': cached_tokens,
                    'total_tokens': total_tokens
                }
                
                # 收集指标
                collector = get_metrics_collector(lambda: db)
                collector.collect_conversation_metrics(
                    session_id=session_id,
                    query_text=req.question,
                    response_text=full_response,
                    retrieval_data=retrieval_data,
                    token_data=token_data,
                    model_name='gpt-4',
                    retrieval_method='hybrid'
                )
                
                print(f"[监控] 收集指标成功: session={session_id}, tokens={total_tokens}, time={response_time:.2f}s", flush=True)
                
            except Exception as e:
                print(f"[监控] 收集指标失败: {e}", flush=True)
        
        # 返回会话 ID 给前端
        headers = {"X-Session-ID": session_id}
        return StreamingResponse(generate(), media_type="text/plain; charset=utf-8", headers=headers)
    
    except Exception as e:
        import traceback
        print(f"[对话] 失败：{str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=f"AI 调用失败：{str(e)}")


@router.post("/ai/session/list")
def get_session_list(req: SessionListRequest = None,
                     db: Session = Depends(get_db)):
    """获取会话列表"""
    try:
        user_id = req.user_id if req else None
        sessions = memory_manager.get_session_list(user_id)
        
        return Response(
            content=json.dumps({
                "code": settings.RES_CODE["200"],
                "msg": "获取成功",
                "data": sessions
            }, ensure_ascii=False),
            media_type="application/json"
        )
    except Exception as e:
        print(f"[会话列表] 失败：{str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"获取会话列表失败：{str(e)}")


@router.post("/ai/session/switch")
def switch_session(req: SessionSwitchRequest,
                   db: Session = Depends(get_db)):
    """切换会话"""
    try:
        old_session_id = req.old_session_id
        new_session_id = req.new_session_id
        user_id = req.user_id
        
        # 切换会话
        memory_manager.switch_session(old_session_id, new_session_id, user_id)
        
        # 恢复历史对话
        history = memory_manager.resume_session(new_session_id)
        
        return Response(
            content=json.dumps({
                "code": settings.RES_CODE["200"],
                "msg": "切换成功",
                "data": {
                    "session_id": new_session_id,
                    "history": history
                }
            }, ensure_ascii=False),
            media_type="application/json"
        )
    except Exception as e:
        print(f"[会话切换] 失败：{str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"切换会话失败：{str(e)}")


@router.post("/ai/session/history")
def get_session_history(req: ChatHistoryRequest,
                        db: Session = Depends(get_db)):
    """获取会话历史记录"""
    try:
        session_id = req.session_id
        history = memory_manager.resume_session(session_id)
        
        return Response(
            content=json.dumps({
                "code": settings.RES_CODE["200"],
                "msg": "获取成功",
                "data": history
            }, ensure_ascii=False),
            media_type="application/json"
        )
    except Exception as e:
        print(f"[历史记录] 失败：{str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"获取历史记录失败：{str(e)}")
