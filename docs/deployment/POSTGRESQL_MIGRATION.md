# MongoDB to PostgreSQL Migration Guide

## Overview

This guide covers the migration from MongoDB to PostgreSQL for the Hear! Hear! Bot due to persistent SSL/TLS connectivity issues with MongoDB Atlas and Python 3.13+.

## Why PostgreSQL?

- **Better Python 3.13+ compatibility**: No SSL/TLS issues with modern Python versions
- **Robust ACID compliance**: Better data consistency and reliability
- **Mature ecosystem**: Well-established tooling and community support
- **Performance**: Better query optimization and indexing
- **JSON support**: PostgreSQL has excellent JSON/JSONB support for flexible data

## Migration Steps

### 1. Install Dependencies

```bash
# Install PostgreSQL packages
pip install asyncpg sqlalchemy[asyncio] psycopg2-binary

# Or use requirements file
pip install -r requirements/production.txt
```

### 2. Database Setup

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE hearhearbot;
CREATE USER botuser WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hearhearbot TO botuser;
\q
```

#### Option B: Cloud PostgreSQL
Popular options:
- **Supabase**: Free tier with 500MB storage
- **Neon**: Serverless PostgreSQL with free tier
- **Railway**: Simple deployment with PostgreSQL
- **DigitalOcean**: Managed PostgreSQL databases

### 3. Environment Configuration

Update your `.env` file:

```env
# Remove MongoDB settings
# MONGODB_CONNECTION_STRING=mongodb+srv://...

# Add PostgreSQL settings
DATABASE_URL=postgresql://username:password@host:port/database

# Or individual settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hearhearbot
POSTGRES_USER=botuser
POSTGRES_PASSWORD=your_password
```

### 4. Code Migration Status

✅ **Completed:**
- Database connection manager rewritten for PostgreSQL
- Configuration updated to support PostgreSQL
- Requirements files updated
- SQLAlchemy models created

⏳ **In Progress:**
- Bot client integration
- Command modules update
- Data migration utilities

❌ **Pending:**
- Full data migration from MongoDB
- Testing and validation
- Documentation updates

## Database Schema

The new PostgreSQL schema includes these main tables:

- `guilds` - Server configuration and settings
- `users` - User data across all guilds  
- `user_settings` - Per-guild user preferences
- `reaction_role_configs` - Reaction role message configurations
- `reaction_roles` - Individual reaction-role mappings
- `timers` - Debate timer information
- `command_logs` - Command usage analytics
- `debate_sessions` - Debate session tracking

## Migration Commands

```bash
# 1. Backup existing MongoDB data (if applicable)
mongodump --uri="your_mongodb_connection_string" --out=backup/

# 2. Install new dependencies
pip install -r requirements/production.txt

# 3. Run database migrations
python -c "
import asyncio
from src.database.postgres_models import create_tables
from src.database.connection import database

async def setup_db():
    if database.engine:
        await create_tables(database.engine)
        print('✅ Database tables created')
    else:
        print('❌ Database not connected')

asyncio.run(setup_db())
"

# 4. Test connection
python -c "
import asyncio
from src.database.connection import database

async def test_db():
    stats = database.get_connection_stats()
    print(f'Database connected: {stats[\"is_connected\"]}')
    print(f'Database type: {stats[\"database_type\"]}')

asyncio.run(test_db())
"
```

## Fallback Strategy

If PostgreSQL setup fails, the bot will:

1. **Continue running** without database features
2. **Log warnings** about missing database connectivity
3. **Provide helpful error messages** for troubleshooting
4. **Maintain core functionality** (Discord commands, timers)

## Troubleshooting

### Connection Issues

```bash
# Test PostgreSQL connection
pg_isready -h localhost -p 5432

# Check if PostgreSQL is running
sudo systemctl status postgresql

# View PostgreSQL logs
sudo journalctl -u postgresql -f
```

### Common Errors

1. **"Database does not exist"**
   ```sql
   CREATE DATABASE hearhearbot;
   ```

2. **"Authentication failed"**
   - Check username/password
   - Verify user permissions
   - Check `pg_hba.conf` settings

3. **"Connection refused"**
   - Ensure PostgreSQL is running
   - Check host/port settings
   - Verify firewall rules

### Configuration Validation

```python
# Test configuration
python -c "
from config.settings import Config
print(f'PostgreSQL URL: {Config.get_postgres_url()}')
print(f'Host: {Config.POSTGRES_HOST}')
print(f'Database: {Config.POSTGRES_DB}')
"
```

## Performance Optimization

### Connection Pooling
```python
# Already configured in connection.py
DATABASE_MIN_POOL_SIZE=5
DATABASE_MAX_POOL_SIZE=20
DATABASE_TIMEOUT=30
```

### Indexing
The schema includes optimized indexes for:
- Guild lookups
- User queries
- Reaction role searches
- Timer operations
- Command analytics

### Query Optimization
- Use SQLAlchemy ORM for complex queries
- Use raw asyncpg for performance-critical operations
- Leverage PostgreSQL's JSON operators for flexible data

## Next Steps

1. **Install PostgreSQL** (local or cloud)
2. **Update environment variables**
3. **Install dependencies**: `pip install -r requirements/production.txt`
4. **Test connection**: Run database connection test
5. **Create tables**: Run migration commands
6. **Verify functionality**: Test bot with PostgreSQL backend

## Support

For issues during migration:

1. Check the troubleshooting section above
2. Review PostgreSQL logs
3. Verify environment configuration
4. Test with minimal connection first

The migration provides better reliability and future-proofs the bot against Python version compatibility issues.