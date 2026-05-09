"""
Test cases for assign_weights function
"""

from functions import assign_weights

def test_assign_weights_basic():
    """Test basic weight calculation with known input"""
    
    # Test input
    input_tags = {
        "category_tags": ["cafe", "bar"],
        "vibe_tags": ["cozy", "casual"], 
        "special_tags": ["outdoor"],
        "price_tags": ["moderate"]
    }
    
    # Expected response (nested structure)
    expected_weights = {
        "category_tags": {
            "cafe": 0.35, "bar": 0.35, 
            "restaurant": 0.04, "dessert": 0.04, "activity": 0.04, "arcade": 0.04, 
            "cinema": 0.04, "park": 0.04, "shopping": 0.04
        },
        "vibe_tags": {
            "cozy": 0.3, "casual": 0.3, 
            "fancy": 0.06, "aesthetic": 0.06, "lively": 0.06, "quiet": 0.06, 
            "romantic": 0.06, "trendy": 0.06, "family_friendly": 0.06
        },
        "special_tags": {
            "outdoor": 0.4, "date_spot": 0.12, "group_friendly": 0.12, 
            "quick_stop": 0.12, "late_night": 0.12, "indoor": 0.12
        },
        "price_tags": {
            "moderate": 1.0, "affordable": 0.0, "upscale": 0.0
        }
    }
    
    # Get actual weights
    actual_weights = assign_weights(input_tags)
    
    # Compare expected vs actual
    assert actual_weights == expected_weights, f"Expected {expected_weights}, got {actual_weights}"
    
    print("✅ Response matches expected exactly!")
    return True

if __name__ == "__main__":
    print("Running assign_weights tests...")
    test_assign_weights_basic()
    print("🎉 All tests passed!")
