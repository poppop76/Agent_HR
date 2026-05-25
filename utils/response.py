"""
统一返回类
"""
from typing import Any, Optional, List


def resp_ok(msg: str = "操作成功") -> dict:
    """无参成功返回 等价 R.success()"""
    return {
        "code": 200,
        "msg": msg,
        "data": None
    }


def resp_entity(data: Any, msg: str = "查询成功") -> dict:
    """返回单个实体/单个对象 等价 R.success(实体)"""
    return {
        "code": 200,
        "msg": msg,
        "data": data
    }


def resp_page(records: List[Any], total: int, msg: str = "分页查询成功") -> dict:
    """分页多参返回 等价分页VO"""
    return {
        "code": 200,
        "msg": msg,
        "data": {
            "records": records,
            "total": total
        }
    }


def resp_login(token: str, user_info: Any, msg: str = "登录成功") -> dict:
    """登录专属返回 登录专用VO"""
    return {
        "code": 200,
        "msg": msg,
        "data": {
            "token": token,
            "userInfo": user_info
        }
    }


def resp_fail(msg: str = "操作失败", code: int = 500) -> dict:
    """通用失败返回 等价R.error()"""
    return {
        "code": code,
        "msg": msg,
        "data": None
    }


def resp_param_error(msg: str = "参数校验失败") -> dict:
    """参数错误专用返回"""
    return resp_fail(msg=msg, code=400)


def resp_not_found(msg: str = "数据不存在") -> dict:
    """404数据不存在"""
    return resp_fail(msg=msg, code=404)