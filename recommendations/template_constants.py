"""
Template Constants for Recommendation Engine

This module defines template-related constants including:
- Stage-specific category weights for plan generation
- Template scoring weights for selection
- Confidence thresholds for execution behavior
- Template execution behaviors based on confidence
"""

# ============================================================================
# STAGE WEIGHTS FOR PLAN GENERATION
# ============================================================================
PLAN_STAGE_WEIGHTS_2_STAGE = {

    "date_night": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "restaurant": 0.45,
                    "cafe": 0.35,
                    "activity": 0.20
                },
                "vibe_tags": {
                    "romantic": 0.40,
                    "cozy": 0.30,
                    "aesthetic": 0.20,
                    "quiet": 0.10
                },
                "special_tags": {
                    "date_spot": 0.60,
                    "indoor": 0.25,
                    "quick_stop": 0.15
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.45,
                    "bar": 0.30,
                    "cafe": 0.15,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "romantic": 0.35,
                    "fancy": 0.30,
                    "cozy": 0.20,
                    "aesthetic": 0.15
                },
                "special_tags": {
                    "date_spot": 0.55,
                    "indoor": 0.25,
                    "outdoor": 0.20
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "restaurant": 0.40,
                    "cafe": 0.35,
                    "dessert": 0.15,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "romantic": 0.30,
                    "cozy": 0.25,
                    "aesthetic": 0.20,
                    "casual": 0.15,
                    "fancy": 0.10
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "indoor": 0.25,
                    "quick_stop": 0.15,
                    "outdoor": 0.15
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.40,
                    "bar": 0.25,
                    "cafe": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "romantic": 0.30,
                    "fancy": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.15,
                    "casual": 0.10
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "indoor": 0.25,
                    "outdoor": 0.20,
                    "late_night": 0.15
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.35,
                    "restaurant": 0.30,
                    "dessert": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "romantic": 0.20,
                    "cozy": 0.20,
                    "casual": 0.20,
                    "aesthetic": 0.15,
                    "fancy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "date_spot": 0.25,
                    "indoor": 0.20,
                    "quick_stop": 0.20,
                    "outdoor": 0.15,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.35,
                    "activity": 0.25,
                    "cafe": 0.20,
                    "bar": 0.20
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "romantic": 0.20,
                    "quiet": 0.15,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "fancy": 0.10
                },
                "special_tags": {
                    "date_spot": 0.25,
                    "late_night": 0.20,
                    "indoor": 0.20,
                    "quick_stop": 0.15,
                    "outdoor": 0.10,
                    "group_friendly": 0.10
                }
            }
        }
    },

    "social_energy": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.45,
                    "bar": 0.35,
                    "restaurant": 0.20
                },
                "vibe_tags": {
                    "lively": 0.35,
                    "trendy": 0.25,
                    "casual": 0.15,
                    "aesthetic": 0.10,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.35,
                    "late_night": 0.35,
                    "outdoor": 0.10,
                    "indoor": 0.10,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            },
            "stage_2": {
                "category_tags": {
                    "bar": 0.35,
                    "activity": 0.20,
                    "restaurant": 0.20
                },
                "vibe_tags": {
                    "lively": 0.35,
                    "trendy": 0.25,
                    "fancy": 0.15,
                    "casual": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "late_night": 0.40,
                    "group_friendly": 0.30,
                    "indoor": 0.10,
                    "outdoor": 0.10,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.40,
                    "bar": 0.30,
                    "restaurant": 0.20,
                    "cafe": 0.10
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.30,
                    "late_night": 0.30,
                    "outdoor": 0.15,
                    "indoor": 0.15,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            },
            "stage_2": {
                "category_tags": {
                    "bar": 0.40,
                    "dessert": 0.25,
                    "restaurant": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.20,
                    "fancy": 0.15,
                    "casual": 0.20,
                    "aesthetic": 0.15
                },
                "special_tags": {
                    "late_night": 0.35,
                    "group_friendly": 0.25,
                    "indoor": 0.15,
                    "outdoor": 0.15,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.35,
                    "restaurant": 0.25,
                    "bar": 0.20,
                    "cafe": 0.20
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "casual": 0.20,
                    "trendy": 0.15,
                    "cozy": 0.15,
                    "aesthetic": 0.15,
                    "fancy": 0.10
                },
                "special_tags": {
                    "group_friendly": 0.25,
                    "late_night": 0.20,
                    "outdoor": 0.15,
                    "indoor": 0.15,
                    "quick_stop": 0.15,
                    "date_spot": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "bar": 0.30,
                    "dessert": 0.25,
                    "activity": 0.25,
                    "restaurant": 0.20
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "casual": 0.20,
                    "trendy": 0.15,
                    "cozy": 0.15,
                    "fancy": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "late_night": 0.30,
                    "group_friendly": 0.20,
                    "indoor": 0.15,
                    "outdoor": 0.15,
                    "quick_stop": 0.10,
                    "date_spot": 0.10
                }
            }
        }
    },

    "easy_living": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.45,
                    "restaurant": 0.30,
                    "shopping": 0.15,
                    "dessert": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.40,
                    "casual": 0.30,
                    "quiet": 0.15,
                    "aesthetic": 0.10,
                    "fancy": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.40,
                    "indoor": 0.30,
                    "outdoor": 0.20,
                    "group_friendly": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.40,
                    "cafe": 0.35,
                    "shopping": 0.15,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.35,
                    "casual": 0.30,
                    "quiet": 0.20,
                    "aesthetic": 0.15
                },
                "special_tags": {
                    "quick_stop": 0.35,
                    "indoor": 0.30,
                    "group_friendly": 0.20,
                    "outdoor": 0.15
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.40,
                    "restaurant": 0.25,
                    "shopping": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "casual": 0.25,
                    "quiet": 0.20,
                    "aesthetic": 0.15,
                    "fancy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "indoor": 0.25,
                    "outdoor": 0.20,
                    "group_friendly": 0.15,
                    "date_spot": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.35,
                    "cafe": 0.30,
                    "shopping": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "casual": 0.25,
                    "quiet": 0.20,
                    "aesthetic": 0.15,
                    "fancy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.35,
                    "shopping": 0.25,
                    "restaurant": 0.20,
                    "activity": 0.20
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "quiet": 0.15,
                    "aesthetic": 0.15,
                    "fancy": 0.15,
                    "trendy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.20,
                    "group_friendly": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.30,
                    "shopping": 0.25,
                    "activity": 0.25,
                    "cafe": 0.20
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "quiet": 0.15,
                    "aesthetic": 0.15,
                    "fancy": 0.15,
                    "trendy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "group_friendly": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            }
        }
    },

    "exploration_mode": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.50,
                    "shopping": 0.20,
                    "cafe": 0.20,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.35,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "lively": 0.10,
                    "fancy": 0.10
                },
                "special_tags": {
                    "outdoor": 0.40,
                    "group_friendly": 0.30,
                    "indoor": 0.20,
                    "quick_stop": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.30,
                    "cafe": 0.30,
                    "activity": 0.20,
                    "shopping": 0.20
                },
                "vibe_tags": {
                    "aesthetic": 0.30,
                    "casual": 0.25,
                    "trendy": 0.20,
                    "cozy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "outdoor": 0.35,
                    "group_friendly": 0.30,
                    "quick_stop": 0.20,
                    "indoor": 0.15
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.45,
                    "shopping": 0.20,
                    "cafe": 0.20,
                    "restaurant": 0.15
                },
                "vibe_tags": {
                    "aesthetic": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "lively": 0.15,
                    "cozy": 0.10
                },
                "special_tags": {
                    "outdoor": 0.35,
                    "group_friendly": 0.25,
                    "indoor": 0.20,
                    "quick_stop": 0.15,
                    "date_spot": 0.05
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.25,
                    "activity": 0.25,
                    "cafe": 0.25,
                    "shopping": 0.25
                },
                "vibe_tags": {
                    "aesthetic": 0.25,
                    "casual": 0.25,
                    "trendy": 0.20,
                    "cozy": 0.15,
                    "quiet": 0.15
                },
                "special_tags": {
                    "outdoor": 0.30,
                    "group_friendly": 0.25,
                    "quick_stop": 0.20,
                    "indoor": 0.15,
                    "date_spot": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.40,
                    "shopping": 0.25,
                    "restaurant": 0.20,
                    "cafe": 0.15
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "lively": 0.15,
                    "cozy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "outdoor": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.20,
                    "quick_stop": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.25,
                    "activity": 0.25,
                    "shopping": 0.25,
                    "cafe": 0.25
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "cozy": 0.15,
                    "quiet": 0.15,
                    "lively": 0.10
                },
                "special_tags": {
                    "outdoor": 0.25,
                    "group_friendly": 0.20,
                    "quick_stop": 0.20,
                    "indoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            }
        }
    },

    "social_cafe_crawl": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.60,
                    "dessert": 0.20,
                    "shopping": 0.10,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.35,
                    "aesthetic": 0.30,
                    "casual": 0.20,
                    "trendy": 0.10,
                    "quiet": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.40,
                    "quick_stop": 0.30,
                    "indoor": 0.20,
                    "outdoor": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.40,
                    "cafe": 0.35,
                    "activity": 0.15,
                    "shopping": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "aesthetic": 0.25,
                    "casual": 0.25,
                    "trendy": 0.15,
                    "quiet": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.35,
                    "quick_stop": 0.30,
                    "indoor": 0.20,
                    "outdoor": 0.15
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.50,
                    "dessert": 0.20,
                    "shopping": 0.15,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "aesthetic": 0.25,
                    "casual": 0.20,
                    "trendy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "group_friendly": 0.35,
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.05
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.35,
                    "cafe": 0.30,
                    "activity": 0.20,
                    "shopping": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "aesthetic": 0.25,
                    "casual": 0.25,
                    "trendy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "group_friendly": 0.30,
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.45,
                    "shopping": 0.20,
                    "dessert": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "quiet": 0.15,
                    "fancy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.25,
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            },
            "stage_2": {
                "category_tags": {
                    "dessert": 0.30,
                    "activity": 0.25,
                    "shopping": 0.25,
                    "cafe": 0.20
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "quiet": 0.15,
                    "fancy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.25,
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            }
        }
    },

    "fun_date": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.65,
                    "arcade": 0.20,
                    "bar": 0.10,
                    "cafe": 0.05
                },
                "vibe_tags": {
                    "lively": 0.40,
                    "trendy": 0.30,
                    "casual": 0.20,
                    "romantic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "indoor": 0.30,
                    "late_night": 0.15,
                    "outdoor": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "bar": 0.45,
                    "cafe": 0.25,
                    "dessert": 0.20,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "romantic": 0.35,
                    "lively": 0.25,
                    "trendy": 0.25,
                    "casual": 0.15
                },
                "special_tags": {
                    "date_spot": 0.50,
                    "late_night": 0.25,
                    "indoor": 0.15,
                    "outdoor": 0.10
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.55,
                    "arcade": 0.20,
                    "bar": 0.15,
                    "cafe": 0.10
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.25,
                    "casual": 0.25,
                    "romantic": 0.20
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "indoor": 0.30,
                    "late_night": 0.20,
                    "outdoor": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "bar": 0.35,
                    "cafe": 0.30,
                    "dessert": 0.20,
                    "restaurant": 0.15
                },
                "vibe_tags": {
                    "romantic": 0.30,
                    "lively": 0.25,
                    "trendy": 0.25,
                    "casual": 0.20
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "indoor": 0.25,
                    "late_night": 0.20,
                    "outdoor": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.40,
                    "bar": 0.25,
                    "arcade": 0.20,
                    "restaurant": 0.15
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "casual": 0.25,
                    "trendy": 0.25,
                    "romantic": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.35,
                    "indoor": 0.25,
                    "late_night": 0.20,
                    "outdoor": 0.15,
                    "group_friendly": 0.05
                }
            },
            "stage_2": {
                "category_tags": {
                    "bar": 0.30,
                    "cafe": 0.25,
                    "dessert": 0.25,
                    "activity": 0.20
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "romantic": 0.25,
                    "lively": 0.25,
                    "trendy": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "indoor": 0.25,
                    "late_night": 0.20,
                    "outdoor": 0.15
                }
            }
        }
    },

    "retail_therapy": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "shopping": 0.65,
                    "cafe": 0.20,
                    "dessert": 0.10,
                    "restaurant": 0.05
                },
                "vibe_tags": {
                    "aesthetic": 0.40,
                    "trendy": 0.30,
                    "fancy": 0.20,
                    "casual": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.45,
                    "indoor": 0.35,
                    "outdoor": 0.20
                }
            },
            "stage_2": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.35,
                    "shopping": 0.15,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.35,
                    "cozy": 0.25,
                    "casual": 0.20,
                    "fancy": 0.15,
                    "quiet": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.40,
                    "indoor": 0.35,
                    "group_friendly": 0.15,
                    "outdoor": 0.10
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "shopping": 0.55,
                    "cafe": 0.20,
                    "restaurant": 0.15,
                    "dessert": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "fancy": 0.15,
                    "cozy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.35,
                    "indoor": 0.30,
                    "outdoor": 0.20,
                    "group_friendly": 0.15
                }
            },
            "stage_2": {
                "category_tags": {
                    "cafe": 0.35,
                    "dessert": 0.30,
                    "shopping": 0.20,
                    "restaurant": 0.15
                },
                "vibe_tags": {
                    "aesthetic": 0.30,
                    "cozy": 0.25,
                    "casual": 0.20,
                    "fancy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.35,
                    "indoor": 0.30,
                    "group_friendly": 0.20,
                    "outdoor": 0.15
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "shopping": 0.45,
                    "cafe": 0.20,
                    "restaurant": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "cozy": 0.15,
                    "fancy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "indoor": 0.25,
                    "outdoor": 0.20,
                    "group_friendly": 0.15,
                    "date_spot": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "cafe": 0.30,
                    "dessert": 0.25,
                    "shopping": 0.25,
                    "activity": 0.20
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "quiet": 0.15,
                    "fancy": 0.15,
                    "trendy": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10
                }
            }
        }
    }
}


PLAN_STAGE_WEIGHTS_3_STAGE = {
    "date_night": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.30,
                    "restaurant": 0.30
                },
                "vibe_tags": {
                    "romantic": 0.40,
                    "cozy": 0.30,
                    "aesthetic": 0.20,
                    "quiet": 0.10
                },
                "special_tags": {
                    "date_spot": 0.60,
                    "indoor": 0.25,
                    "quick_stop": 0.15
                }
            },

            "stage_2": {
                "category_tags": {
                    "restaurant": 0.55,
                    "bar": 0.30,
                    "dessert": 0.15
                },
                "vibe_tags": {
                    "romantic": 0.35,
                    "fancy": 0.30,
                    "cozy": 0.20,
                    "aesthetic": 0.15
                },
                "special_tags": {
                    "date_spot": 0.55,
                    "indoor": 0.25,
                    "outdoor": 0.20
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.45,
                    "bar": 0.35,
                    "cafe": 0.20
                },
                "vibe_tags": {
                    "cozy": 0.40,
                    "romantic": 0.35,
                    "quiet": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.50,
                    "late_night": 0.30,
                    "indoor": 0.20
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.35,
                    "dessert": 0.25,
                    "restaurant": 0.25,
                    "bar": 0.15
                },
                "vibe_tags": {
                    "romantic": 0.30,
                    "cozy": 0.25,
                    "aesthetic": 0.20,
                    "casual": 0.15,
                    "fancy": 0.10
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "indoor": 0.25,
                    "quick_stop": 0.15,
                    "outdoor": 0.15
                }
            },

            "stage_2": {
                "category_tags": {
                    "restaurant": 0.45,
                    "bar": 0.25,
                    "dessert": 0.20,
                    "cafe": 0.10
                },
                "vibe_tags": {
                    "romantic": 0.30,
                    "fancy": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.15,
                    "casual": 0.10
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "indoor": 0.25,
                    "outdoor": 0.20,
                    "late_night": 0.15
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.40,
                    "bar": 0.35,
                    "cafe": 0.25
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "romantic": 0.25,
                    "quiet": 0.20,
                    "casual": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "late_night": 0.25,
                    "indoor": 0.20,
                    "quick_stop": 0.15
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.25,
                    "dessert": 0.20,
                    "restaurant": 0.20,
                    "bar": 0.15,
                    "activity": 0.10,
                    "shopping": 0.10
                },
                "vibe_tags": {
                    "romantic": 0.20,
                    "cozy": 0.20,
                    "casual": 0.20,
                    "aesthetic": 0.15,
                    "fancy": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "date_spot": 0.25,
                    "indoor": 0.20,
                    "quick_stop": 0.20,
                    "outdoor": 0.15,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "restaurant": 0.30,
                    "bar": 0.25,
                    "dessert": 0.20,
                    "cafe": 0.10,
                    "activity": 0.10,
                    "shopping": 0.05
                },
                "vibe_tags": {
                    "romantic": 0.20,
                    "fancy": 0.15,
                    "cozy": 0.20,
                    "casual": 0.20,
                    "aesthetic": 0.15,
                    "quiet": 0.10
                },
                "special_tags": {
                    "date_spot": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.20,
                    "late_night": 0.20,
                    "group_friendly": 0.10,
                    "quick_stop": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.35,
                    "bar": 0.25,
                    "cafe": 0.20,
                    "activity": 0.10,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "romantic": 0.20,
                    "quiet": 0.15,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "fancy": 0.10
                },
                "special_tags": {
                    "date_spot": 0.25,
                    "late_night": 0.20,
                    "indoor": 0.20,
                    "quick_stop": 0.15,
                    "outdoor": 0.10,
                    "group_friendly": 0.10
                }
            }
        }
    },

    "social_energy": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.35,
                    "bar": 0.30,
                    "restaurant": 0.15,
                    "cafe": 0.10,
                    "dessert": 0.07,
                    "shopping": 0.03
                },
                "vibe_tags": {
                    "lively": 0.35,
                    "trendy": 0.25,
                    "casual": 0.15,
                    "aesthetic": 0.10,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.35,
                    "late_night": 0.35,
                    "outdoor": 0.10,
                    "indoor": 0.10,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "bar": 0.40,
                    "activity": 0.30,
                    "restaurant": 0.15,
                    "dessert": 0.10,
                    "cafe": 0.03,
                    "shopping": 0.02
                },
                "vibe_tags": {
                    "lively": 0.35,
                    "trendy": 0.25,
                    "fancy": 0.15,
                    "casual": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "late_night": 0.40,
                    "group_friendly": 0.30,
                    "indoor": 0.10,
                    "outdoor": 0.10,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "bar": 0.45,
                    "dessert": 0.25,
                    "activity": 0.20,
                    "restaurant": 0.07,
                    "cafe": 0.02,
                    "shopping": 0.01
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "late_night": 0.45,
                    "group_friendly": 0.25,
                    "quick_stop": 0.10,
                    "indoor": 0.10,
                    "outdoor": 0.05,
                    "date_spot": 0.05
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.30,
                    "bar": 0.25,
                    "restaurant": 0.20,
                    "cafe": 0.15,
                    "dessert": 0.03,
                    "shopping": 0.02
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.30,
                    "late_night": 0.30,
                    "outdoor": 0.15,
                    "indoor": 0.15,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "bar": 0.35,
                    "activity": 0.25,
                    "restaurant": 0.20,
                    "dessert": 0.15,
                    "cinema": 0.03,
                    "cafe": 0.01,
                    "shopping": 0.01
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.20,
                    "fancy": 0.15,
                    "casual": 0.20,
                    "aesthetic": 0.15
                },
                "special_tags": {
                    "late_night": 0.35,
                    "group_friendly": 0.25,
                    "indoor": 0.15,
                    "outdoor": 0.15,
                    "quick_stop": 0.05,
                    "date_spot": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "bar": 0.40,
                    "dessert": 0.20,
                    "activity": 0.20,
                    "restaurant": 0.15,
                    "cinema": 0.03,
                    "cafe": 0.01,
                    "shopping": 0.01
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "trendy": 0.20,
                    "casual": 0.25,
                    "aesthetic": 0.15,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "late_night": 0.40,
                    "group_friendly": 0.20,
                    "quick_stop": 0.15,
                    "indoor": 0.15,
                    "outdoor": 0.05,
                    "date_spot": 0.05
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.25,
                    "bar": 0.20,
                    "restaurant": 0.20,
                    "cafe": 0.20,
                    "cinema": 0.08,
                    "dessert": 0.05,
                    "shopping": 0.02
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "trendy": 0.20,
                    "casual": 0.25,
                    "aesthetic": 0.15,
                    "fancy": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.25,
                    "late_night": 0.25,
                    "outdoor": 0.20,
                    "indoor": 0.15,
                    "quick_stop": 0.10,
                    "date_spot": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "bar": 0.30,
                    "activity": 0.20,
                    "restaurant": 0.20,
                    "dessert": 0.20,
                    "cafe": 0.03,
                    "shopping": 0.02
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "trendy": 0.20,
                    "fancy": 0.15,
                    "casual": 0.25,
                    "aesthetic": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "late_night": 0.30,
                    "group_friendly": 0.20,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "quick_stop": 0.10,
                    "date_spot": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "bar": 0.35,
                    "dessert": 0.20,
                    "activity": 0.20,
                    "restaurant": 0.15,
                    "cafe": 0.03,
                    "shopping": 0.02
                },
                "vibe_tags": {
                    "lively": 0.20,
                    "trendy": 0.20,
                    "casual": 0.25,
                    "aesthetic": 0.15,
                    "fancy": 0.15,
                    "cozy": 0.05
                },
                "special_tags": {
                    "late_night": 0.35,
                    "group_friendly": 0.20,
                    "quick_stop": 0.15,
                    "indoor": 0.15,
                    "outdoor": 0.10,
                    "date_spot": 0.05
                }
            }
        }
    },

    "easy_living": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.30,
                    "restaurant": 0.20,
                    "shopping": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.35,
                    "quiet": 0.25,
                    "casual": 0.15,
                    "aesthetic": 0.10,
                    "romantic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.30,
                    "quick_stop": 0.25,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "restaurant": 0.35,
                    "cafe": 0.30,
                    "shopping": 0.15,
                    "dessert": 0.10,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "quiet": 0.25,
                    "casual": 0.15,
                    "romantic": 0.15,
                    "aesthetic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.30,
                    "outdoor": 0.20,
                    "quick_stop": 0.20,
                    "date_spot": 0.10,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.35,
                    "cafe": 0.35,
                    "shopping": 0.15,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.35,
                    "quiet": 0.30,
                    "romantic": 0.15,
                    "casual": 0.10,
                    "aesthetic": 0.05,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.30,
                    "quick_stop": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.10,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.25,
                    "shopping": 0.15,
                    "restaurant": 0.12,
                    "activity": 0.08
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "quiet": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "romantic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.25,
                    "quick_stop": 0.25,
                    "outdoor": 0.20,
                    "date_spot": 0.10,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "restaurant": 0.30,
                    "cafe": 0.25,
                    "shopping": 0.15,
                    "dessert": 0.15,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "quiet": 0.25,
                    "casual": 0.20,
                    "romantic": 0.15,
                    "aesthetic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.25,
                    "outdoor": 0.20,
                    "quick_stop": 0.20,
                    "date_spot": 0.15,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.30,
                    "cafe": 0.30,
                    "shopping": 0.15,
                    "activity": 0.15,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "quiet": 0.25,
                    "romantic": 0.15,
                    "casual": 0.15,
                    "aesthetic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.25,
                    "quick_stop": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.15,
                    "group_friendly": 0.10,
                    "late_night": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.35,
                    "dessert": 0.20,
                    "shopping": 0.15,
                    "restaurant": 0.15,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "quiet": 0.20,
                    "casual": 0.25,
                    "aesthetic": 0.15,
                    "romantic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.20,
                    "quick_stop": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.15,
                    "group_friendly": 0.15,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "restaurant": 0.25,
                    "cafe": 0.25,
                    "shopping": 0.15,
                    "dessert": 0.15,
                    "activity": 0.20
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "quiet": 0.20,
                    "casual": 0.25,
                    "romantic": 0.15,
                    "aesthetic": 0.10,
                    "family_friendly": 0.05
                },
                "special_tags": {
                    "indoor": 0.20,
                    "outdoor": 0.20,
                    "quick_stop": 0.20,
                    "date_spot": 0.15,
                    "group_friendly": 0.15,
                    "late_night": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.25,
                    "cafe": 0.25,
                    "shopping": 0.20,
                    "activity": 0.20,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "quiet": 0.20,
                    "romantic": 0.15,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "family_friendly": 0.10
                },
                "special_tags": {
                    "indoor": 0.20,
                    "quick_stop": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.15,
                    "group_friendly": 0.15,
                    "late_night": 0.10
                }
            }
        }
    },

    "exploration_mode": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.45,
                    "cafe": 0.20,
                    "restaurant": 0.15,
                    "shopping": 0.10,
                    "dessert": 0.05,
                    "bar": 0.05
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "quiet": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "outdoor": 0.40,
                    "quick_stop": 0.25,
                    "group_friendly": 0.15,
                    "indoor": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "activity": 0.50,
                    "restaurant": 0.20,
                    "cafe": 0.15,
                    "shopping": 0.10,
                    "dessert": 0.03,
                    "bar": 0.02
                },
                "vibe_tags": {
                    "lively": 0.35,
                    "trendy": 0.25,
                    "casual": 0.15,
                    "aesthetic": 0.10,
                    "quiet": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "outdoor": 0.45,
                    "quick_stop": 0.25,
                    "group_friendly": 0.15,
                    "indoor": 0.10,
                    "late_night": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "cafe": 0.30,
                    "dessert": 0.25,
                    "activity": 0.20,
                    "shopping": 0.15,
                    "restaurant": 0.07,
                    "bar": 0.03
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "quiet": 0.15,
                    "trendy": 0.10,
                    "lively": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "outdoor": 0.15,
                    "late_night": 0.10
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.40,
                    "cafe": 0.20,
                    "restaurant": 0.15,
                    "shopping": 0.15,
                    "dessert": 0.05,
                    "bar": 0.05
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.15,
                    "quiet": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "outdoor": 0.35,
                    "quick_stop": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.15,
                    "late_night": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "activity": 0.45,
                    "restaurant": 0.20,
                    "cafe": 0.15,
                    "shopping": 0.10,
                    "dessert": 0.07,
                    "bar": 0.03
                },
                "vibe_tags": {
                    "lively": 0.30,
                    "trendy": 0.25,
                    "casual": 0.20,
                    "aesthetic": 0.10,
                    "quiet": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "outdoor": 0.35,
                    "quick_stop": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.15,
                    "late_night": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "cafe": 0.25,
                    "dessert": 0.25,
                    "activity": 0.20,
                    "shopping": 0.15,
                    "restaurant": 0.10,
                    "bar": 0.05
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "quiet": 0.15,
                    "trendy": 0.10,
                    "lively": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "outdoor": 0.20,
                    "late_night": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "activity": 0.35,
                    "cafe": 0.20,
                    "restaurant": 0.15,
                    "shopping": 0.15,
                    "dessert": 0.08,
                    "bar": 0.07
                },
                "vibe_tags": {
                    "lively": 0.20,
                    "trendy": 0.20,
                    "casual": 0.20,
                    "aesthetic": 0.15,
                    "quiet": 0.15,
                    "cozy": 0.10
                },
                "special_tags": {
                    "outdoor": 0.30,
                    "quick_stop": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.15,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "activity": 0.40,
                    "restaurant": 0.20,
                    "cafe": 0.15,
                    "shopping": 0.10,
                    "dessert": 0.10,
                    "bar": 0.05
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "trendy": 0.20,
                    "casual": 0.20,
                    "aesthetic": 0.15,
                    "quiet": 0.15,
                    "cozy": 0.05
                },
                "special_tags": {
                    "outdoor": 0.30,
                    "quick_stop": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.15,
                    "late_night": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "cafe": 0.25,
                    "dessert": 0.25,
                    "activity": 0.20,
                    "shopping": 0.15,
                    "restaurant": 0.10,
                    "bar": 0.05
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "quiet": 0.15,
                    "trendy": 0.10,
                    "lively": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "outdoor": 0.15,
                    "late_night": 0.15
                }
            }
        }
    },

    "social_cafe_crawl": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.50,
                    "dessert": 0.20,
                    "shopping": 0.10,
                    "activity": 0.10,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.30,
                    "casual": 0.20,
                    "cozy": 0.20,
                    "trendy": 0.15,
                    "lively": 0.10,
                    "quiet": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "group_friendly": 0.25,
                    "indoor": 0.15,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.25,
                    "restaurant": 0.15,
                    "activity": 0.10,
                    "shopping": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.30,
                    "casual": 0.20,
                    "cozy": 0.20,
                    "trendy": 0.15,
                    "lively": 0.10,
                    "quiet": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.30,
                    "quick_stop": 0.25,
                    "indoor": 0.15,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.35,
                    "cafe": 0.35,
                    "activity": 0.10,
                    "shopping": 0.10,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "aesthetic": 0.25,
                    "casual": 0.20,
                    "trendy": 0.15,
                    "quiet": 0.10,
                    "lively": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "group_friendly": 0.25,
                    "indoor": 0.15,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.45,
                    "dessert": 0.20,
                    "shopping": 0.12,
                    "activity": 0.12,
                    "restaurant": 0.11
                },
                "vibe_tags": {
                    "aesthetic": 0.25,
                    "casual": 0.25,
                    "cozy": 0.20,
                    "trendy": 0.15,
                    "lively": 0.10,
                    "quiet": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "group_friendly": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "cafe": 0.35,
                    "dessert": 0.25,
                    "restaurant": 0.20,
                    "activity": 0.12,
                    "shopping": 0.08
                },
                "vibe_tags": {
                    "aesthetic": 0.25,
                    "casual": 0.25,
                    "cozy": 0.20,
                    "trendy": 0.15,
                    "lively": 0.10,
                    "quiet": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.25,
                    "quick_stop": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.30,
                    "cafe": 0.30,
                    "activity": 0.15,
                    "shopping": 0.15,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.20,
                    "aesthetic": 0.25,
                    "casual": 0.25,
                    "trendy": 0.15,
                    "quiet": 0.10,
                    "lively": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "group_friendly": 0.25,
                    "indoor": 0.20,
                    "outdoor": 0.15,
                    "date_spot": 0.10,
                    "late_night": 0.05
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.20,
                    "shopping": 0.15,
                    "activity": 0.15,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.20,
                    "casual": 0.25,
                    "cozy": 0.20,
                    "trendy": 0.15,
                    "lively": 0.15,
                    "quiet": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.20,
                    "group_friendly": 0.20,
                    "indoor": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "cafe": 0.30,
                    "dessert": 0.25,
                    "restaurant": 0.20,
                    "activity": 0.15,
                    "shopping": 0.10
                },
                "vibe_tags": {
                    "aesthetic": 0.20,
                    "casual": 0.25,
                    "cozy": 0.20,
                    "trendy": 0.15,
                    "lively": 0.15,
                    "quiet": 0.05
                },
                "special_tags": {
                    "group_friendly": 0.20,
                    "quick_stop": 0.20,
                    "indoor": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "dessert": 0.25,
                    "cafe": 0.25,
                    "activity": 0.20,
                    "shopping": 0.20,
                    "restaurant": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.20,
                    "aesthetic": 0.20,
                    "casual": 0.25,
                    "trendy": 0.15,
                    "quiet": 0.15,
                    "lively": 0.05
                },
                "special_tags": {
                    "quick_stop": 0.20,
                    "group_friendly": 0.20,
                    "indoor": 0.20,
                    "outdoor": 0.20,
                    "date_spot": 0.10,
                    "late_night": 0.10
                }
            }
        }
    },

    "fun_date": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.50,
                    "restaurant": 0.30,
                    "dessert": 0.20
                },
                "vibe_tags": {
                    "romantic": 0.35,
                    "casual": 0.30,
                    "trendy": 0.20,
                    "aesthetic": 0.15
                },
                "special_tags": {
                    "date_spot": 0.50,
                    "indoor": 0.30,
                    "quick_stop": 0.20
                }
            },
            "stage_2": {
                "category_tags": {
                    "activity": 0.65,
                    "arcade": 0.25,
                    "bar": 0.10
                },
                "vibe_tags": {
                    "lively": 0.40,
                    "trendy": 0.30,
                    "casual": 0.20,
                    "romantic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "indoor": 0.30,
                    "late_night": 0.25
                }
            },
            "stage_3": {
                "category_tags": {
                    "bar": 0.55,
                    "dessert": 0.25,
                    "cafe": 0.20
                },
                "vibe_tags": {
                    "romantic": 0.40,
                    "lively": 0.25,
                    "trendy": 0.20,
                    "casual": 0.15
                },
                "special_tags": {
                    "date_spot": 0.50,
                    "late_night": 0.30,
                    "indoor": 0.20
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.40,
                    "restaurant": 0.35,
                    "dessert": 0.25
                },
                "vibe_tags": {
                    "casual": 0.30,
                    "romantic": 0.25,
                    "aesthetic": 0.25,
                    "trendy": 0.20
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "indoor": 0.30,
                    "quick_stop": 0.25
                }
            },
            "stage_2": {
                "category_tags": {
                    "activity": 0.55,
                    "arcade": 0.25,
                    "bar": 0.20
                },
                "vibe_tags": {
                    "lively": 0.35,
                    "trendy": 0.30,
                    "casual": 0.20,
                    "romantic": 0.15
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "indoor": 0.35,
                    "late_night": 0.25
                }
            },
            "stage_3": {
                "category_tags": {
                    "bar": 0.45,
                    "dessert": 0.30,
                    "cafe": 0.25
                },
                "vibe_tags": {
                    "romantic": 0.35,
                    "lively": 0.25,
                    "trendy": 0.25,
                    "casual": 0.15
                },
                "special_tags": {
                    "date_spot": 0.45,
                    "late_night": 0.35,
                    "indoor": 0.20
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "cafe": 0.35,
                    "restaurant": 0.30,
                    "activity": 0.20,
                    "dessert": 0.15
                },
                "vibe_tags": {
                    "casual": 0.30,
                    "romantic": 0.20,
                    "aesthetic": 0.20,
                    "lively": 0.15,
                    "trendy": 0.15
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "indoor": 0.30,
                    "quick_stop": 0.20,
                    "outdoor": 0.10
                }
            },
            "stage_2": {
                "category_tags": {
                    "activity": 0.40,
                    "arcade": 0.25,
                    "bar": 0.20,
                    "restaurant": 0.15
                },
                "vibe_tags": {
                    "lively": 0.25,
                    "casual": 0.25,
                    "trendy": 0.25,
                    "romantic": 0.25
                },
                "special_tags": {
                    "date_spot": 0.35,
                    "indoor": 0.30,
                    "late_night": 0.20,
                    "outdoor": 0.15
                }
            },
            "stage_3": {
                "category_tags": {
                    "bar": 0.35,
                    "dessert": 0.30,
                    "cafe": 0.20,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "casual": 0.25,
                    "romantic": 0.25,
                    "lively": 0.25,
                    "trendy": 0.15,
                    "aesthetic": 0.10
                },
                "special_tags": {
                    "date_spot": 0.40,
                    "late_night": 0.30,
                    "indoor": 0.20,
                    "outdoor": 0.10
                }
            }
        }
    },

    "retail_therapy": {
        "high": {
            "stage_1": {
                "category_tags": {
                    "shopping": 0.60,
                    "cafe": 0.20,
                    "dessert": 0.10,
                    "restaurant": 0.05,
                    "activity": 0.05
                },
                "vibe_tags": {
                    "trendy": 0.35,
                    "aesthetic": 0.30,
                    "casual": 0.20,
                    "lively": 0.10,
                    "cozy": 0.05
                },
                "special_tags": {
                    "outdoor": 0.35,
                    "group_friendly": 0.25,
                    "quick_stop": 0.20,
                    "indoor": 0.15,
                    "date_spot": 0.05
                }
            },

            "stage_2": {
                "category_tags": {
                    "shopping": 0.50,
                    "cafe": 0.15,
                    "dessert": 0.10,
                    "restaurant": 0.10,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "casual": 0.30,
                    "trendy": 0.25,
                    "aesthetic": 0.20,
                    "lively": 0.15,
                    "cozy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "outdoor": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.15,
                    "date_spot": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "cafe": 0.40,
                    "dessert": 0.30,
                    "shopping": 0.15,
                    "restaurant": 0.10,
                    "activity": 0.05
                },
                "vibe_tags": {
                    "cozy": 0.35,
                    "casual": 0.25,
                    "aesthetic": 0.20,
                    "trendy": 0.10,
                    "lively": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.40,
                    "indoor": 0.30,
                    "group_friendly": 0.15,
                    "date_spot": 0.10,
                    "outdoor": 0.05
                }
            }
        },

        "medium": {
            "stage_1": {
                "category_tags": {
                    "shopping": 0.55,
                    "cafe": 0.20,
                    "dessert": 0.10,
                    "restaurant": 0.10,
                    "activity": 0.05
                },
                "vibe_tags": {
                    "trendy": 0.30,
                    "casual": 0.25,
                    "aesthetic": 0.25,
                    "lively": 0.10,
                    "cozy": 0.10
                },
                "special_tags": {
                    "outdoor": 0.30,
                    "group_friendly": 0.25,
                    "quick_stop": 0.20,
                    "indoor": 0.15,
                    "date_spot": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "shopping": 0.45,
                    "cafe": 0.15,
                    "dessert": 0.10,
                    "restaurant": 0.15,
                    "activity": 0.15
                },
                "vibe_tags": {
                    "casual": 0.30,
                    "trendy": 0.25,
                    "aesthetic": 0.20,
                    "lively": 0.15,
                    "cozy": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "outdoor": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.20,
                    "date_spot": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "cafe": 0.35,
                    "dessert": 0.30,
                    "shopping": 0.15,
                    "restaurant": 0.15,
                    "activity": 0.05
                },
                "vibe_tags": {
                    "cozy": 0.30,
                    "casual": 0.25,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "lively": 0.10
                },
                "special_tags": {
                    "quick_stop": 0.30,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "date_spot": 0.15,
                    "outdoor": 0.10
                }
            }
        },

        "low": {
            "stage_1": {
                "category_tags": {
                    "shopping": 0.45,
                    "cafe": 0.20,
                    "dessert": 0.10,
                    "restaurant": 0.15,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "casual": 0.30,
                    "trendy": 0.20,
                    "aesthetic": 0.20,
                    "lively": 0.15,
                    "cozy": 0.15
                },
                "special_tags": {
                    "outdoor": 0.25,
                    "group_friendly": 0.25,
                    "quick_stop": 0.20,
                    "indoor": 0.20,
                    "date_spot": 0.10
                }
            },

            "stage_2": {
                "category_tags": {
                    "shopping": 0.40,
                    "cafe": 0.15,
                    "dessert": 0.10,
                    "restaurant": 0.15,
                    "activity": 0.20
                },
                "vibe_tags": {
                    "casual": 0.30,
                    "trendy": 0.20,
                    "aesthetic": 0.20,
                    "lively": 0.15,
                    "cozy": 0.15
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "outdoor": 0.25,
                    "group_friendly": 0.20,
                    "indoor": 0.20,
                    "date_spot": 0.10
                }
            },

            "stage_3": {
                "category_tags": {
                    "cafe": 0.35,
                    "dessert": 0.25,
                    "shopping": 0.15,
                    "restaurant": 0.15,
                    "activity": 0.10
                },
                "vibe_tags": {
                    "cozy": 0.25,
                    "casual": 0.25,
                    "aesthetic": 0.20,
                    "trendy": 0.15,
                    "lively": 0.15
                },
                "special_tags": {
                    "quick_stop": 0.25,
                    "indoor": 0.25,
                    "group_friendly": 0.20,
                    "date_spot": 0.15,
                    "outdoor": 0.15
                }
            }
        }
    }
}


# ============================================================================
# TEMPLATE SELECTION CONSTANTS
# ============================================================================

# Template selection score weights
TEMPLATE_SCORE_WEIGHTS = {
    'category': 0.35,
    'vibe': 0.40,
    'special': 0.25,
    'context': 0.00
}

# Confidence thresholds for template execution
CONFIDENCE_THRESHOLDS = {
    'high': 0.65,
    'medium': 0.40,
    'low': 0.0
}

# Template execution behaviors based on confidence
TEMPLATE_EXECUTION_BEHAVIORS = {
    'high': {
        'description': 'Strict template execution',
        'tag_selection_strictness': 1.0,  # 0.0 (random) to 1.0 (strict)
        'retry_count': 3,
        'venue_score_boost': 0.3
    },
    'medium': {
        'description': 'Flexible template execution',
        'tag_selection_strictness': 0.7,
        'retry_count': 2,
        'venue_score_boost': 0.15
    },
    'low': {
        'description': 'Hybrid adaptive generation',
        'tag_selection_strictness': 0.4,
        'retry_count': 1,
        'venue_score_boost': 0.0
    }
}


# ============================================================================
# TEMPLATE SUMMARY LINES FOR HEADLINES
# =====
TEMPLATE_COPY = {
    "date_night": {
        "titles": [
            "A slower evening in {area}",
            "Just the two of you in {area}",
            "Unhurried nights in {area}"
        ],
        "descriptions": [
            "The kind of evening that feels effortless.",
            "Spots that make the evening feel easy.",
            "Quiet enough to actually talk."
        ]
    },

    "social_energy": {
        "titles": [
            "Night out in {area}",
            "The energy is right in {area}",
            "Where the night goes in {area}"
        ],
        "descriptions": [
            "The kind of night that builds on itself.",
            "Good energy from the first stop to the last.",
            "The kind of evening you don't want to end."
        ]
    },

    "easy_living": {
        "titles": [
            "No rush in {area}",
            "Taking it easy in {area}",
            "A gentle evening in {area}"
        ],
        "descriptions": [
            "The kind of evening that doesn't need a plan.",
            "Slow and easy, exactly as it should be.",
            "No agenda. Just a good time."
        ]
    },

    "exploration_mode": {
        "titles": [
            "Something new in {area}",
            "Off the usual path in {area}",
            "Loose plans in {area}"
        ],
        "descriptions": [
            "The kind of evening that surprises you.",
            "For nights with no fixed destination.",
            "Something a little different every time."
        ]
    },

    "social_cafe_crawl": {
        "titles": [
            "Coffee and good company in {area}",
            "Slow mornings, slower afternoons in {area}",
            "Cafe to cafe in {area}"
        ],
        "descriptions": [
            "The kind of afternoon that stretches into evening.",
            "Good coffee, better conversation.",
            "Unhurried and easy, just how it should be."
        ]
    },

    "retail_therapy": {
        "titles": [
            "Browse and breathe in {area}",
            "Shops and stops in {area}",
            "A little of everything in {area}"
        ],
        "descriptions": [
            "The kind of afternoon that earns a coffee.",
            "Slow down, look around, enjoy it.",
            "No rush. Just a good afternoon out."
        ]
    }
}