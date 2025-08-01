#!/usr/bin/env python3
"""
Test script for ResearcherAgent integration with onboarding data and Qloo insights
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'workflows', 'core'))

from researcher_agent import ResearcherAgent

def test_researcher_integration():
    """Test the comprehensive research functionality"""
    
    # Initialize the researcher agent
    researcher = ResearcherAgent(
        name="test_researcher",
        initial_state={},
        context={}
    )
    
    print("🧪 Testing ResearcherAgent Integration")
    print("=" * 50)
    
    # Test 1: Get onboarding profile (will use latest if available)
    print("\n1. Testing onboarding profile retrieval...")
    profile = researcher.get_onboarding_profile()
    
    if "error" in profile:
        print(f"❌ Error: {profile['error']}")
        print("💡 Make sure you have completed onboarding and the database is set up")
    else:
        print("✅ Onboarding profile retrieved successfully")
        print(f"   Brand: {profile.get('raw_data', {}).get('brand_name', 'N/A')}")
        print(f"   Industry: {profile.get('raw_data', {}).get('industry', 'N/A')}")
    
    # Test 2: Conduct comprehensive research
    print("\n2. Testing comprehensive research...")
    research_result = researcher.conduct_comprehensive_research()
    
    if "error" in research_result:
        print(f"❌ Research Error: {research_result['error']}")
    elif research_result.get('success'):
        print("✅ Comprehensive research completed successfully!")
        print(f"   Onboarding ID: {research_result.get('onboarding_id', 'N/A')}")
        print(f"   Campaign Insights: {len(research_result.get('campaign_insights', ''))} characters")
        print(f"   Campaign Plan: {len(research_result.get('campaign_plan', ''))} characters")
        
        # Show a preview of the insights
        insights = research_result.get('campaign_insights', '')
        if insights:
            print(f"\n📊 Campaign Insights Preview:")
            print(insights[:300] + "..." if len(insights) > 300 else insights)
    else:
        print("⚠️  Research completed with partial results")
        print(f"   Error: {research_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_researcher_integration() 