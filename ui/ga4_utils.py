try:
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    from google.analytics.admin_v1beta.types import ListPropertiesRequest
    from google.oauth2.credentials import Credentials
    GOOGLE_ANALYTICS_AVAILABLE = True
except ImportError:
    GOOGLE_ANALYTICS_AVAILABLE = False
    print("Warning: Google Analytics modules not available. GA4 features will be disabled.")

def get_user_properties(credentials):
    if not GOOGLE_ANALYTICS_AVAILABLE:
        return []
        
    client = AnalyticsAdminServiceClient(credentials=credentials)

    # This gets all properties the user has access to
    # this is my account ID, I won't actually be using it in the code, find out how to get the account ID dynamically
    request = ListPropertiesRequest(filter="parent:accounts/346725716")
    properties = client.list_properties(request=request)

    prop_list = []
    for prop in properties:
        prop_list.append({
            "property_id": prop.name.split("/")[-1],
            "display_name": prop.display_name,
            "property_name": prop.name,
        })

    return prop_list
