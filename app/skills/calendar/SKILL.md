# Calendar Management Skill

## Skill Description

This skill enables calendar event management through natural language conversation.


## Capabilities

### 1. Create Events
Add new calendar events with title, time, description, and location.

**Examples:**
- "帮我添加一个明天下午3点的会议"
- "创建一个下周一上午10点到11点的项目评审会议"
- "Add a meeting tomorrow at 3 PM"

### 2. List Events
Query and display calendar events with various filters.

**Examples:**
- "显示今天的所有日程"
- "查看本周的会议安排"
- "Show me all events"

### 3. Update Events
Modify existing calendar events.

**Examples:**
- "把明天的会议时间改到下午4点"
- "更新项目评审会议的地点为会议室B"
- "Change the meeting time to 4 PM"

### 4. Delete Events
Remove calendar evnets.

**Examples:**
- "删除今天下午3点的会议"
- "取消所有明天的安排"
- "Delete the project review meeting"

## Available Tools

### create_event
Creates a new calendar event.

**Parameters:**
- `title` (string, required): Event title.
- `start_time` (datetime, required): Start time in ISO 8601 format.
- `end_time` (datetime, required): End time in ISO 8601 format.
- `description` (string, optional): Event description.
- `location` (string, optional): Event location.

**Returns: ** Created event with ID

### list_events
Lists calendar events with optional filtering.

**Parameters:**
- `start_date` (datetime, optional): Filter events from this date.
- `end_date` (datetime, optional): Filter events until this date.
- `keyword` (string, optional): Search in title and description.

**Returns: ** List of matching events.

### update_event
Updates an existing calendar event.

**Parameters:**
- `event_id` (string, required)P: Event ID to update.
- `title` (string, optional): New title.
- `start_time` (datetime, optional): New start time.
- `end_time` (datetime, optional): New end time.
- `description` (string, optional): New description.
- `location` (string, optional): New location.

**Returns: ** Updated event.

### delete_event
Deletes a calendar event.

**Parameters:**
- `event_id` (string, required): Event ID to delete.

**Returns: ** Success confirmation.

## Usage Guidelines

1. **Time Parsing**: When users mention relative times like "明天"、"下周一", convert them to absolute datetime
2. **Default Duration**: If end time not specified, assume 1 hour duration
3. **Confirmation**: Always confirm after creating/updating/deleting events
4. **Error Handling**: Provide clear error messages when operations fail
5. **Context Awareness**: Use conversation history to resolve ambiguous references

## Example Workflow
```
User: "帮我安排明天下午2点的团队会议"
Assistant: [Calls create_event with calculated datetime]
Assistant: "好的，我已经为您创建了明天(3月21日)下午2点到3点的团队会议。"
```