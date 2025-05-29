#  Setting Up Postgres MCP Pro with Claude Desktop (Developer Mode Enabled)

##  Objective

To integrate [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp) into Claude Desktop using Docker. This setup enables Claude to analyze and interact with a live PostgreSQL database through its Model Context Protocol (MCP) layer.

---

##  Use Case

Postgres MCP Pro is designed to support developers and AI assistants in performing intelligent database operations such as:

* SQL query optimization
* Index analysis and recommendation
* Schema health monitoring
* Safer SQL execution with context awareness
* AI-assisted database debugging

This integration is ideal for backend developers, data engineers, or AI developers who want enhanced database reasoning capabilities in an IDE-like workflow.

---

## Environment Requirements

* Docker installed and running
* Claude Desktop installed
* PostgreSQL instance accessible locally
* Developer Mode enabled in Claude Desktop

---

## PostgreSQL Configuration

The following configuration was used for the PostgreSQL database:

```properties
datasource.url=jdbc:postgresql://localhost:9991/mainschema
username=postgres
password=admin
```

---

##  Claude Desktop Configuration

### File Location

Modify `claude_desktop_config.json`. Location varies by OS:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Updated JSON Configuration

```json
{
  "mcpServers": {
    "postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DATABASE_URI",
        "crystaldba/postgres-mcp",
        "--access-mode=unrestricted"
      ],
      "env": {
        "DATABASE_URI": "postgresql://postgres:admin@host.docker.internal:9991/mainschema"
      }
    }
  },
  "git": {
    "command": "docker",
    "args": [
      "run",
      "--rm",
      "-i",
      "--mount", "type=bind,src=/Users/username/Desktop,dst=/projects/Desktop",
      "--mount", "type=bind,src=/path/to/other/allowed/dir,dst=/projects/other/allowed/dir,ro",
      "--mount", "type=bind,src=/path/to/file.txt,dst=/projects/path/to/file.txt",
      "mcp/git"
    ]
  }
}
```

**Note:** `host.docker.internal` is used for Docker to communicate with localhost in macOS and Windows. For Linux, this should be replaced with `localhost`.

---

## 🧪 Execution Steps

1. Pull the Docker image:

   ```bash
   docker pull crystaldba/postgres-mcp
   ```

2. Update `claude_desktop_config.json` as shown above.

3. Enable **Developer Mode** in Claude Desktop from settings.

4. Restart Claude Desktop. Upon restart, the **Tools** tab should appear automatically.

5. Manually handle any advanced CLAUDE UI interactions or internal configuration steps not documented here.

---

## 🔗 Reference

* Official Repository: [https://github.com/crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp)

---
## Claude Conversation Log:

---

## 1. Database Health Check

### User Request
> "Check the health of my database and identify any issues."

### Actions Performed
- Comprehensive database health analysis using `analyze_db_health` with all health checks enabled
- Evaluated: indexes, connections, vacuum, sequences, replication, buffer cache, and constraints

### Results Found
**Healthy Components:**
- **Indexes**: No invalid, duplicate, or bloated indexes detected
- **Connections**: 7 active connections, 0 idle connections - healthy pool
- **Transaction Management**: No tables at risk of transaction ID wraparound
- **Sequences**: All sequences operating within healthy usage levels
- **Constraints**: No invalid constraints found
- **Replication**: Running as primary database (no replicas configured)

**Issues Identified:**
- **Unused Index**: `idx_department_id` on table `indexed_table` 
  - Never been scanned (0 times)
  - Uses 0.0MB of space
  - Consider review for potential removal

**Missing Data:**
- Buffer cache statistics unavailable (likely `pg_stat_statements` extension not enabled)

### Recommendations Provided
1. Review the unused index for potential removal
2. Enable `pg_stat_statements` extension for better performance visibility
3. Implement regular health monitoring schedule

---

## 2. Database Structure Exploration

### User Request
> "list out all the data bases -> all the schemas and all the tables"

### Actions Performed
- Listed all database schemas using `list_schemas`
- Enumerated tables in each user schema using `list_objects`
- Categorized system vs user schemas

### Database Structure Discovered

#### System Schemas (PostgreSQL Internal)
- `information_schema` - Standard SQL information schema
- `pg_catalog` - PostgreSQL system catalog  
- `pg_toast` - TOAST storage for large attributes

#### User Schemas & Tables

**airbnb_clone Schema (8 tables)**
- `airbnb_user` - User accounts
- `authority` - User permissions/roles
- `booking` - Reservation data
- `databasechangelog` - Migration history
- `databasechangeloglock` - Migration lock table
- `listing` - Property listings
- `listing_picture` - Property images
- `user_authority` - User-role mappings

**labschema Schema (7 tables)**
- `indexed_table` - Test table with indexes
- `my_entity` - Generic entity table
- `non_indexed_table` - Test table without indexes
- `stream_note` - Stream processing notes

**📋 public Schema (16 tables)**
- `app_user` - Application users
- `employee` - Employee records
- `employee_skills` - Employee skill mappings
- `fic_book` - Fiction book catalog
- `flusers` - FL users
- `incident` - Incident tracking
- `inventory_item` - Inventory management
- `item` - Generic items
- `land_registry_price_paid_uk` - UK property transaction data
- `product` - Product catalog
- `product_description` - Product descriptions
- `productol`, `productr`, `productx` - Product variant tables
- `trigger_log` - Database trigger logs
- `xstudents_table` - Student records

**🌍 world Schema (1 table)**
- `employees` - Employee data

### Summary Statistics
- **Total Schemas**: 7 (4 user + 3 system)
- **Total User Tables**: 32 tables
- **Largest Schema**: public (16 tables)
- **Application Domains**: Airbnb clone, testing/lab, business data, geographic data

---

## 3. Data Insertion Operation

### User Request
> "under mainschema database -> labschema schmea there is a table labschema.stream_note add some dummy unique data to it"

### Actions Performed
1. **Table Structure Analysis**
   - Used `get_object_details` to examine `labschema.stream_note` table schema
   - Identified columns: `id` (bigint PK), `added_date` (timestamp), `content` (varchar), `is_live` (boolean), `title` (varchar)

2. **Data Insertion**
   - Inserted 10 unique dummy records with realistic data engineering/stream processing content
   - Used sequential IDs (1-10) with dates spanning January 2024
   - Mixed `is_live` values (7 true, 3 false)

### Inserted Data Records
1. **Stream Pipeline Setup** - Kafka + Flink pipeline configuration
2. **Fraud Detection Implementation** - Flink CEP for fraud detection
3. **Windowing Aggregations** - Tumbling windows for metrics
4. **Checkpoint Optimization** - Fault tolerance improvements
5. **Beam Integration** - Apache Beam with Flink runner
6. **Recommendation Engine** - Real-time collaborative filtering
7. **Monitoring Setup** - Prometheus + Grafana dashboards
8. **Exactly-Once Processing** - Financial transaction consistency
9. **Schema Evolution** - Avro schema compatibility
10. **Performance Tuning** - Cluster optimization

### Verification
- Confirmed successful insertion of 10 records
- Noted existing records (IDs 54-58) were already present
- Total records after insertion: 15

---

## 4. Data Deletion Operation

### User Request
> "cool , remove the data with id 1"

### Actions Performed
- Executed `DELETE FROM labschema.stream_note WHERE id = 1`
- Removed the "Stream Pipeline Setup" record

### Results
- **Before**: 15 total records (IDs 1-10, 54-58)
- **After**: 14 total records (IDs 2-10, 54-58)
- **Minimum ID changed**: From 1 to 2
- **Maximum ID unchanged**: 58

---

## 5. Data Update Operation

### User Request
> "cool can we update an data 5	2024-01-19 11:30:00.000	Integrated Apache Beam with Flink runner for cross-platform compatibility. Testing batch and stream processing unified model.	false	Beam Integration this one and add title as Beam INtegration updated"

### Actions Performed
- Updated record with ID 5 using `UPDATE` statement
- Changed title from "Beam Integration" to "Beam Integration updated"
- All other fields remained unchanged

### Updated Record Details
- **ID**: 5
- **Title**: "Beam Integration updated" ← Changed
- **Added Date**: 2024-01-19 11:30:00 (unchanged)
- **Content**: "Integrated Apache Beam with Flink runner for cross-platform compatibility. Testing batch and stream processing unified model." (unchanged)
- **Is Live**: false (unchanged)

---

## Final Database State

### labschema.stream_note Table
- **Total Records**: 14
- **ID Range**: 2-10, 54-58
- **Recent Changes**: 
  - Deleted ID 1 ("Stream Pipeline Setup")
  - Updated ID 5 title to "Beam Integration updated"
  - Added 9 new dummy records (IDs 2-10, excluding deleted ID 1)

### Session Impact
- Successfully demonstrated database health monitoring
- Comprehensive schema exploration completed
- Data manipulation operations (INSERT, DELETE, UPDATE) executed successfully
- All operations verified through follow-up queries

---

## Technical Notes
- Database: PostgreSQL
- Tools Used: Database management functions for health checks, schema exploration, and SQL execution
- Data Engineering Focus: Inserted realistic stream processing and Apache Flink-related dummy data
- All operations included proper verification steps