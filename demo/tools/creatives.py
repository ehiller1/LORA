"""Creative generation with policy compliance."""

import random
from typing import List, Dict
from .policy import PolicyChecker


class CreativeGenerator:
    """Generate ad copy variants."""
    
    def __init__(self):
        """Initialize creative generator."""
        self.policy_checker = PolicyChecker()
        
        # Templates by tone
        self.templates = {
            'professional': {
                'headlines': [
                    "Premium {product} - Quality You Can Trust",
                    "Discover {product} - Professional Grade",
                    "Elevate Your Experience with {product}",
                    "{product} - Excellence in Every Detail",
                    "Transform Your Space with {product}"
                ],
                'bodies': [
                    "Experience superior quality with our {product}. Designed for professionals who demand the best. Shop now and discover the difference.",
                    "Our {product} combines innovation with reliability. Trusted by experts worldwide. Limited time offer - order today.",
                    "Upgrade to {product} and experience unmatched performance. Premium materials, exceptional craftsmanship. Available now.",
                    "Introducing {product} - where quality meets innovation. Engineered for excellence. Explore our collection today.",
                    "{product} delivers outstanding results every time. Professional-grade quality at competitive prices. Shop the collection."
                ]
            },
            'casual': {
                'headlines': [
                    "Love Your New {product}!",
                    "Get {product} Today",
                    "{product} You'll Actually Use",
                    "Your Perfect {product} Awaits",
                    "Say Hello to {product}"
                ],
                'bodies': [
                    "Ready to upgrade? Our {product} is exactly what you need. Easy to use, built to last. Check it out now!",
                    "Looking for {product}? We've got you covered. Great quality, even better prices. Shop now and save!",
                    "Meet your new favorite {product}. Simple, stylish, and super practical. Get yours today!",
                    "Why settle for less? Our {product} has everything you want. Browse the collection and find your match!",
                    "Time for a change? Try our {product}. You're going to love it. Order now and see for yourself!"
                ]
            },
            'urgent': {
                'headlines': [
                    "Limited Time: {product} Sale",
                    "Don't Miss Out on {product}",
                    "Last Chance: {product} Deal",
                    "Act Now: {product} Special",
                    "Hurry: {product} Going Fast"
                ],
                'bodies': [
                    "This deal won't last! Get {product} now before it's gone. Limited quantities available. Order today!",
                    "Time is running out on our {product} promotion. Don't wait - shop now and save big!",
                    "Final hours to grab {product} at this price. Stock is limited. Secure yours now!",
                    "Flash sale alert! {product} at unbeatable prices. Act fast - offer ends soon!",
                    "Your chance to save on {product} ends tonight. Don't miss this opportunity. Shop now!"
                ]
            },
            'premium': {
                'headlines': [
                    "Luxury {product} Collection",
                    "Exclusive {product} Experience",
                    "Artisan {product} - Handcrafted",
                    "Designer {product} Selection",
                    "Prestige {product} Line"
                ],
                'bodies': [
                    "Indulge in our luxury {product} collection. Meticulously crafted, exceptionally refined. Experience true elegance.",
                    "Discover the art of {product}. Each piece is a masterwork of design and craftsmanship. Explore our exclusive collection.",
                    "Elevate your lifestyle with our premium {product}. Sophisticated design, uncompromising quality. Available in select styles.",
                    "Our {product} represents the pinnacle of luxury. Exquisite materials, timeless design. Reserve yours today.",
                    "Experience {product} reimagined. Where heritage meets innovation. Explore our curated collection."
                ]
            }
        }
        
        # Product name variations
        self.product_names = {
            'SKU-001': 'Wireless Headphones',
            'SKU-002': 'Smart Watch',
            'SKU-003': 'Coffee Maker',
            'SKU-007': 'Yoga Mat',
            'SKU-010': 'Blender',
            'SKU-018': 'Desk Lamp',
            'SKU-023': 'Backpack',
            'SKU-031': 'Running Shoes',
            'SKU-042': 'Water Bottle',
            'SKU-055': 'Notebook Set'
        }
    
    def generate(
        self,
        skus: List[str],
        retailer: str,
        tone: str = 'professional',
        num_variants: int = 2
    ) -> List[Dict]:
        """
        Generate creative variants.
        
        Args:
            skus: List of SKU IDs
            retailer: Retailer identifier
            tone: Creative tone
            num_variants: Number of variants per SKU
        
        Returns:
            List of creative dicts
        """
        creatives = []
        
        tone_lower = tone.lower()
        templates = self.templates.get(tone_lower, self.templates['professional'])
        
        for sku in skus:
            product_name = self.product_names.get(sku, 'Product')
            
            for _ in range(num_variants):
                # Generate headline and body
                headline = random.choice(templates['headlines']).format(product=product_name)
                body = random.choice(templates['bodies']).format(product=product_name)
                
                # Check policy compliance
                policy_result = self.policy_checker.check_creative(headline, body, retailer)
                
                creative = {
                    'sku': sku,
                    'product_name': product_name,
                    'headline': headline,
                    'body': body,
                    'tone': tone,
                    'retailer': retailer,
                    'policy_pass': policy_result['pass'],
                    'policy_reasons': policy_result['reasons']
                }
                
                creatives.append(creative)
        
        return creatives
    
    def fix_violations(self, creative: Dict) -> Dict:
        """
        Attempt to fix policy violations.
        
        Args:
            creative: Creative dict with violations
        
        Returns:
            Fixed creative dict
        """
        headline = creative['headline']
        body = creative['body']
        retailer = creative['retailer']
        
        policy = self.policy_checker.get_policy_summary(retailer)
        
        # Fix disallowed terms
        disallowed = policy.get('disallowed_terms', [])
        replacements = {
            'guaranteed': 'quality',
            'miracle': 'amazing',
            'free': 'complimentary',
            'best': 'top',
            '#1': 'leading'
        }
        
        for term in disallowed:
            if term in replacements:
                headline = headline.replace(term, replacements[term])
                body = body.replace(term, replacements[term])
        
        # Truncate if too long
        max_headline = policy.get('max_headline_length', 100)
        max_body = policy.get('max_body_length', 300)
        
        if len(headline) > max_headline:
            headline = headline[:max_headline-3] + '...'
        
        if len(body) > max_body:
            body = body[:max_body-3] + '...'
        
        # Add required disclaimers
        required = policy.get('required_disclaimers', [])
        for disclaimer in required:
            if disclaimer.lower() not in body.lower():
                body += f" {disclaimer}."
        
        # Re-check
        policy_result = self.policy_checker.check_creative(headline, body, retailer)
        
        return {
            **creative,
            'headline': headline,
            'body': body,
            'policy_pass': policy_result['pass'],
            'policy_reasons': policy_result['reasons'],
            'fixed': True
        }
