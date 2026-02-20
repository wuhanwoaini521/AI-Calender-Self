from typing import List, Dict, Any, Optional
from datetime import datetime


class MCPTools:
    """MCP 工具定义 - 定义可供Claude调用的工具"""
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """
        获取所有工具的定义 （符合Anthropic Tool use格式）
        Returns:
            List[Dict[str, Any]]: 工具定义列表
        """
        
        return [
            {
                "name": "create_event",
                "description": "创建一个新的日历事件。用于添加会议、约会或其他日程安排。支持单次事件和重复事件。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "事件标题，例如：'团队会议', '项目评审'"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "开始时间，ISO 8601 格式，例如：'2024-03-20T14:00:00'"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "结束时间，ISO 8601 格式，例如：'2024-03-20T15:00:00'"
                        },
                        "description": {
                            "type": "string",
                            "description": "事件描述(可选)"
                        },
                        "location": {
                            "type": "string",
                            "description": "事件地点(可选), 例如: '会议室A', '线上'"
                        },
                        "recurrence_rule": {
                            "type": "object",
                            "description": "重复规则(可选)，用于创建重复事件如每周例会",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["daily", "weekly", "monthly"],
                                    "description": "重复类型: daily-每天, weekly-每周, monthly-每月"
                                },
                                "days": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                                    },
                                    "description": "每周重复的星期几（仅weekly类型使用），例如：[\"monday\", \"tuesday\", \"friday\"]"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "重复结束日期，ISO 8601 格式（日期部分即可），例如：'2024-06-30'"
                                }
                            },
                            "required": ["type"]
                        }
                    },
                    "required": ["title", "start_time", "end_time"]
                }
            },
            {
                "name": "list_events",
                "description": "查询日历事件列表。可以按时间范围或关键词筛选事件。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "开始日期筛选（可选），ISO 8601 格式"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期筛选（可选），ISO 8601 格式"
                        },
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词（可选），在标题和描述中搜索"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "update_event",
                "description": "更新已存在的日历事件。可以修改标题、时间、描述或地点。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "要更新的事件ID"
                        },
                        "title": {
                            "type": "string",
                            "description": "新的标题（可选）"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "新的开始时间（可选），ISO 8601 格式"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "新的结束时间（可选），ISO 8601 格式"
                        },
                        "description": {
                            "type": "string",
                            "description": "新的描述（可选）"
                        },
                        "location": {
                            "type": "string",
                            "description": "新的地点（可选）"
                        }
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "delete_event",
                "description": "删除日历事件。如果是重复事件的父事件，会删除所有相关实例。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "要删除的事件ID"
                        },
                        "delete_all_instances": {
                            "type": "boolean",
                            "description": "如果是重复事件，是否删除所有实例（可选，默认为true）"
                        }
                    },
                    "required": ["event_id"]
                }
            }
        ]
