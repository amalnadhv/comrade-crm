import shutil
from datetime import datetime

def backup_db():
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy("crm.db", filename)
    return filename
