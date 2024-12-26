from pydantic import BaseModel


class SqlLogInfo(BaseModel):
    sql: str
    """sql语句"""


class SqlText(BaseModel):
    """
    sql语句
    """

    sql: str


class Column(BaseModel):
    """
    列
    """

    column_name: str
    """列名"""
    data_type: str
    """数据类型"""
    max_length: int | None
    """最大长度"""
    is_nullable: str
    """是否可为空"""
