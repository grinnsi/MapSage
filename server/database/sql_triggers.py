from server.database.models import GeneralOption, PreRenderedJson

# All trigger variables are an array of two strings. The first string is the DROP TRIGGER statement, and the second string is the CREATE TRIGGER statement.

# Trigger for updating the landing page json, if title or description is updated
TRIGGER_PRE_RENDER_LANDING_PAGE = [f"""
DROP TRIGGER IF EXISTS pre_render_landing_page;
""", f"""
CREATE TRIGGER IF NOT EXISTS pre_render_landing_page
    AFTER UPDATE OF value ON "{GeneralOption.__tablename__}"
    BEGIN
        UPDATE {PreRenderedJson.__tablename__} SET value = 
            json_patch(value, json_object(
                'title', (SELECT value FROM "{GeneralOption.__tablename__}" WHERE "key" = 'service_title'),
                'description', (SELECT value FROM "{GeneralOption.__tablename__}" WHERE "key" = 'service_description')    
            ))
        WHERE "key" = 'landing_page';
    END;
"""]

def get_all_triggers() -> list[list[str]]:
    return [
        TRIGGER_PRE_RENDER_LANDING_PAGE,
    ]