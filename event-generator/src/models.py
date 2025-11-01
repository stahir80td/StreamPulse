"""
Data models and content catalog for event generation
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ContentItem:
    """Content catalog item"""
    id: str
    title: str
    type: str
    category: str
    size_mb: int
    price: float
    popularity: float  # Weight for random selection (0.0-1.0)

# Content Catalog - Simulates Apple's digital store
CONTENT_CATALOG = [
    ContentItem(
        id="mov_avengers_2",
        title="Avengers: Endgame 2",
        type="movie",
        category="action",
        size_mb=4200,
        price=19.99,
        popularity=0.50  # 50% of events
    ),
    ContentItem(
        id="mov_taylor_swift",
        title="Taylor Swift: Eras Tour",
        type="music_doc",
        category="music",
        size_mb=3200,
        price=14.99,
        popularity=0.30  # 30% of events
    ),
    ContentItem(
        id="mov_batman",
        title="The Batman Returns",
        type="movie",
        category="action",
        size_mb=3800,
        price=19.99,
        popularity=0.15  # 15% of events
    ),
    ContentItem(
        id="mov_barbie_2",
        title="Barbie 2",
        type="movie",
        category="comedy",
        size_mb=2900,
        price=17.99,
        popularity=0.05  # 5% of events (less popular)
    ),
]

# Geographic Regions
REGIONS = [
    ("US-California", "San Francisco"),
    ("US-California", "Los Angeles"),
    ("US-Texas", "Austin"),
    ("US-NewYork", "New York City"),
    ("EU-London", "London"),
    ("EU-Paris", "Paris"),
    ("EU-Berlin", "Berlin"),
    ("ASIA-Tokyo", "Tokyo"),
    ("ASIA-Seoul", "Seoul"),
    ("ASIA-Mumbai", "Mumbai"),
]

# Device Types
DEVICES = [
    ("iPhone 15 Pro", "iOS 18.1"),
    ("iPhone 14", "iOS 18.0"),
    ("iPad Pro", "iPadOS 18.0"),
    ("iPad Air", "iPadOS 17.6"),
    ("Apple TV 4K", "tvOS 18.0"),
    ("MacBook Pro", "macOS 14.5"),
]

# Connection Types
CONNECTION_TYPES = ["wifi", "5g", "4g", "ethernet"]

# Error Types (for failed downloads)
ERROR_TYPES = [
    {"code": "cdn_timeout", "message": "CDN server timeout - try again"},
    {"code": "network_error", "message": "Network connection lost during download"},
    {"code": "disk_full", "message": "Insufficient storage space on device"},
    {"code": "auth_failed", "message": "Authentication token expired"},
]