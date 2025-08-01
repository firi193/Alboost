import requests
import os
import openai
import json
from dotenv import load_dotenv


load_dotenv() 

openai.api_key = os.getenv("OPENAI_API_KEY_")

# Debug: Check if QLOO_API_KEY is loaded
qloo_api_key = os.getenv("QLOO_API_KEY")
if not qloo_api_key:
    print("⚠️  WARNING: QLOO_API_KEY not found in environment variables!")
    print("   Make sure your .env file contains: QLOO_API_KEY=your_api_key_here")
else:
    print(f"✅ QLOO_API_KEY loaded: {qloo_api_key[:10]}...")

headers = {
    "x-api-key": qloo_api_key,
    "Content-Type": "application/json"
}

# Debug: Print the actual headers being used
print(f"🔍 Headers being used: {headers}")


def gpt_extract_audience_signals(campaign_text):
    prompt = f"""
You are an expert campaign strategist.

From the following campaign text, extract **key audience targeting signals**, formatted as JSON with the following keys:

- Demographics: (e.g., age groups, gender, generation, etc.)
- Interests / Values: (e.g., sustainability, clean design, wellness — short phrases only)
- Behaviors: (e.g., purchase habits, engagement patterns)
- Locations: (e.g., urban cities, coasts, regions)
- Cultural References: (e.g., brand names, pop culture, hashtags, visual aesthetics)

Rules:
- Normalize hashtags (e.g., "#cleanbeauty" → "clean beauty") before adding them to Interests or Cultural References.
- Only include brands, artists, hashtags, or visual aesthetics in Cultural References.
- Avoid overly general terms (e.g., "design") unless contextually meaningful.
- Do NOT fabricate information not present in the text.
- Keep all lists concise, with no more than 5–7 items per category.
- Return only valid JSON.

Campaign text:
\"\"\"{campaign_text}\"\"\"

Return as a JSON dictionary.
"""
    print("\n\n\nin gpt_extract_audience_signals\n\n\n")
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    # Parse the JSON string output into a Python dictionary
    return json.loads(response.choices[0].message.content.strip())





def search_and_filter_tags(search_term):
  print("\n\n\nin search_and_filter_tags\n\n\n")
  url = "https://hackathon.api.qloo.com/v2/tags"
  tag_ids=[]
  audience_ids=[]

  params = {
  "filter.query": search_term
  }

  try:
    print(f"🔍 Making request to: {url}")
    print(f"🔍 With headers: {headers}")
    print(f"🔍 With params: {params}")
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    tags_data=response.json()['results']['tags']
    
    # Fix: Add proper error handling for tag ID extraction
    all_tag_ids = []
    for tag in tags_data:
        tag_dict = select_dict_values(['id'], tag)
        if 'id' in tag_dict:
            all_tag_ids.append(tag_dict['id'])

    for tag_id in all_tag_ids:
      if "audience" in tag_id:
        audience_ids.append(tag_id)
      else:
        tag_ids.append(tag_id)

  except requests.exceptions.Timeout:
    print(f"Timeout error for search term: {search_term}")
    return [], []
  except requests.exceptions.RequestException as e:
    print(f"Request error for search term '{search_term}': {e}")
    return [], []
  except Exception as e:
    print(f"Unexpected error for search term '{search_term}': {e}")
    return [], []

  return tag_ids, audience_ids



def select_dict_values(selected_keys, original_dict):
    new_dict = {}
    for key in selected_keys:
        if isinstance(key, str):
            if key in original_dict:
                new_dict[key] = original_dict[key]
        elif isinstance(key, tuple) and len(key) == 2:
            parent_key, child_key = key
            if parent_key in original_dict and isinstance(original_dict[parent_key], dict) and child_key in original_dict[parent_key]:
                 new_dict[child_key] = original_dict[parent_key][child_key]
    return new_dict





def search_entity(search_term):
    print("\n\n\nin search_entity\n\n\n")
    url = "https://hackathon.api.qloo.com/search"
    params = {
        "query": search_term,
        # "types": types
    }
    resp = requests.get(url, headers=headers, params=params)
    print(resp)
    data = resp.json()
    if data and data.get('results') and len(data['results']) > 0:
        return data['results'][0]
    else:
        return None
    




def get_trending_data(entity_ids, start_date, end_date):
  """
  Calls the Qloo Trending API with specified parameters.

  Args:
    params: A dictionary of parameters for the API request.

  Returns:
    The JSON response from the API, or None if the request was unsuccessful.
  """
  print("\n\n\nin get_trending_data\n\n\n")
  url = "https://hackathon.api.qloo.com/v2/trending"
  params = {
      "signal.interests.entities": ",".join(entity_ids),
      "filter.type": "urn:entity:brand",
      "filter.start_date": start_date,
      "filter.end_date": end_date
  }
  response = requests.get(url, headers=headers, params=params) # The params are passed as a dictionary here

  print("Status Code:", response.status_code)
  try:
      data = response.json()
      print("Response JSON:", data)
      return data
  except Exception as e:
      print("Error decoding JSON:", str(e))
      print("Raw response:", response.text)
      return None
  


def get_insights(seed_signals, headers):
    print("\n\n\nin get_insights\n\n\n")
    interests = seed_signals.get('Interests / Values', [])
    cultural_refs = seed_signals.get('Cultural References', [])
    locations = seed_signals.get('Locations', [])
    tag_ids, audience_ids = get_tags_and_audiences(interests)
    entity_ids = get_entities(cultural_refs, headers)

    selected_tags = fetch_tags_insights(tag_ids, audience_ids, headers)
    selected_entities, trending_data = fetch_entities_insights(entity_ids, headers)
    demographics_data=fetch_demographics_insights(tag_ids, audience_ids, entity_ids, headers, locations)

    return selected_tags, selected_entities, trending_data, demographics_data


def get_tags_and_audiences(interests):
    print("\n\n\nin get_tags_and_audiences\n\n\n")
    tag_ids = []
    audience_ids = []
    
    # Limit the number of interests to search to prevent too many API calls
    max_interests = 5
    limited_interests = interests[:max_interests] if interests else []
    
    print(f"🔍 Searching for tags/audiences for {len(limited_interests)} interests: {limited_interests}")
    
    for interest in limited_interests:
        tg_ids, ad_ids = search_and_filter_tags(interest)
        tag_ids.extend(tg_ids)
        audience_ids.extend(ad_ids)
    
    # Remove duplicates
    tag_ids = list(set(tag_ids))
    audience_ids = list(set(audience_ids))
    
    print(f"🔍 Found {len(tag_ids)} unique tags and {len(audience_ids)} unique audiences")
    
    return tag_ids, audience_ids


def get_entities(entities, headers):
    print("\n\n\nin get_entities\n\n\n")
    entity_ids = []
    for entity in entities:
        entity_obj = search_entity(entity)  # assumes headers inside this function
        if entity_obj:
            entity_ids.append(entity_obj['entity_id'])
    return entity_ids


def fetch_tags_insights(tag_ids, audience_ids, headers):
    print("\n\n\nin fetch_tags_insights\n\n\n")
    url = "https://hackathon.api.qloo.com/v2/insights"
    params = {
        "filter.results.tags": ",".join(tag_ids),
        "signal.demographics.audiences": ",".join(audience_ids),
        "filter.type": "urn:tag",
    }

    resp = requests.get(url, headers=headers, params=params)
    tags = resp.json()['results'].get('tags', [])
    selected_tags = [select_dict_values(['name', 'type', 'id'], tag) for tag in tags]
    return selected_tags


def fetch_demographics_insights(tag_ids, audience_ids, entity_ids, headers, locations):
    # print(locations)
    url = "https://hackathon.api.qloo.com/v2/insights"
    params = {
        "signal.interest.tags": ",".join(tag_ids),
        "signal.demographics.audiences": ",".join(audience_ids),
        "signal.interests.entities": ",".join(entity_ids),
        # "filter.tags": "urn:tag:genre:health_and_beauty",
        # "filter.type": "urn:tag
        "filter.type": "urn:demographics",
        "signal.location.query":  ", ".join(locations)
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        demographics=resp.json()['results']['demographics']
        return demographics
    except Exception as e:
        print(f"Error fetching demographics insights: {e}")
        return []



def fetch_entities_insights(entity_ids, headers):
    url = "https://hackathon.api.qloo.com/v2/insights"
    params = {
        "filter.results.entities": ",".join(entity_ids),
        "filter.type": "urn:entity:brand",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        entities = resp.json()['results'].get('entities', [])

        selected_entities = [
            select_dict_values(['name', 'subtype', ('properties', 'short_description')], ent)
            for ent in entities
        ]

        all_trending_data = {}
        for entity in entities:
            entity_id = entity.get('entity_id')
            if entity_id:
                trending = get_trending_data([entity_id], "2025-06-24", "2025-07-24")
                if trending and 'results' in trending:
                    all_trending_data[entity.get('name')] = trending['results'].get('trending', [])

        return selected_entities, all_trending_data
    except Exception as e:
        print(f"Error fetching entities insights: {e}")
        return [], {}




def generate_campaign_insights(audience_profile, product_description, qloo_data, seed_signals):
    print("\n\n\nin generate_campaign_insights\n\n\n")
    # Extracting names and descriptions from Qloo data
    selected_tags_str = ', '.join([tag.get('name', '') for tag in qloo_data.get("selected_tags", [])])
    selected_entities_str = ', '.join([ent.get('name', '') for ent in qloo_data.get("selected_entities", [])])
    # Trending data is a dictionary of lists, need to format this differently
    trending_data_str = ', '.join([f"{k}: {len(v)} trending items" for k, v in qloo_data.get("trending_data", {}).items()])
    # Demographics data is a list of dictionaries, need to format this differently
    demographics_data_str = ', '.join([f"{d.get('name', '')}: {d.get('value', '')}" for d in qloo_data.get("demographics_data", [])])


    prompt = f"""
You are a cultural strategist helping a brand understand its audience.

Audience Profile:
{audience_profile}

Product Description:
{product_description}

Qloo Insights:
- Tags: {selected_tags_str}
- Cultural Entities: {selected_entities_str}
- Trending Topics: {trending_data_str}
- Demographics: {demographics_data_str}

Behavioral Signals:
{', '.join(seed_signals.get("Behaviors", []))}

Instructions:
Analyze the above and summarize:
1. Key cultural and behavioral themes.
2. Audience motivations and values.
3. Trends and cultural touchpoints to leverage.
4. Strategic recommendations for positioning the product.

Output:
- Cultural Insights Summary
- Audience Motivation
- Strategic Positioning Suggestions
"""
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()




def generate_campaign_plan(audience_profile, product_description, campaign_insights):
    print("\n\n\nin generate_campaign_plan\n\n\n")
    prompt = f"""
You are a campaign strategist and copywriter crafting a launch plan for social media.

Audience Profile:
{audience_profile}

Product Description:
{product_description}

Strategic Insights:
{campaign_insights}

Instructions:
Based on the insights and audience values:
1. Create 3 Instagram captions (emotionally resonant, culturally relevant).
2. Include hashtags (based on interests, values, trends).
3. Suggest an SEO-friendly campaign title.
4. Describe the campaign tone/style in detail.
5. List 2–3 content themes/pillars (e.g., “clean beauty,” “social consciousness”).
6. Suggest any influencer or brand collab ideas (if relevant).

Output:
- Captions (3)
- Suggested Hashtags
- SEO Campaign Title
- Tone/Style Summary
- Key Messaging Themes
- Collaboration/Influencer Ideas
"""
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()





def run_full_campaign_generator(audience_profile, product_description, qloo_data, seed_signals):
    insights = generate_campaign_insights(audience_profile, product_description, qloo_data, seed_signals)
    plan = generate_campaign_plan(audience_profile, product_description, insights)
    return {
        "insights": insights,
        "campaign_plan": plan
    }
