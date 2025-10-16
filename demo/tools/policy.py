"""Policy compliance checker."""

import re
from typing import Dict, List


class PolicyChecker:
    """Check ad copy against retailer policies."""
    
    def __init__(self):
        """Initialize policy checker."""
        self.policies = {
            'alpha': {
                'max_headline_length': 80,
                'max_body_length': 250,
                'disallowed_terms': ['guaranteed', 'miracle', 'cure', 'free', 'winner'],
                'required_disclaimers': [],
                'tone': 'professional'
            },
            'beta': {
                'max_headline_length': 60,
                'max_body_length': 200,
                'disallowed_terms': ['best', 'free', 'guaranteed', '#1'],
                'required_disclaimers': ['Terms apply'],
                'tone': 'casual'
            }
        }
    
    def check(self, text: str, retailer_id: str, field: str = 'body') -> Dict:
        """
        Check text against policy.
        
        Args:
            text: Text to check
            retailer_id: Retailer identifier
            field: 'headline' or 'body'
        
        Returns:
            Dict with pass/fail and reasons
        """
        policy = self.policies.get(retailer_id.lower(), {})
        reasons = []
        
        # Check length
        if field == 'headline':
            max_len = policy.get('max_headline_length', 100)
            if len(text) > max_len:
                reasons.append(f"Headline exceeds {max_len} chars ({len(text)} chars)")
        elif field == 'body':
            max_len = policy.get('max_body_length', 300)
            if len(text) > max_len:
                reasons.append(f"Body exceeds {max_len} chars ({len(text)} chars)")
        
        # Check disallowed terms
        disallowed = policy.get('disallowed_terms', [])
        for term in disallowed:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                reasons.append(f"Contains disallowed term: '{term}'")
        
        # Check required disclaimers (for body only)
        if field == 'body':
            required = policy.get('required_disclaimers', [])
            for disclaimer in required:
                if disclaimer.lower() not in text.lower():
                    reasons.append(f"Missing required disclaimer: '{disclaimer}'")
        
        return {
            'pass': len(reasons) == 0,
            'reasons': reasons
        }
    
    def check_creative(self, headline: str, body: str, retailer_id: str) -> Dict:
        """
        Check complete creative.
        
        Args:
            headline: Headline text
            body: Body text
            retailer_id: Retailer identifier
        
        Returns:
            Dict with overall pass/fail and reasons
        """
        headline_result = self.check(headline, retailer_id, 'headline')
        body_result = self.check(body, retailer_id, 'body')
        
        all_reasons = headline_result['reasons'] + body_result['reasons']
        
        return {
            'pass': len(all_reasons) == 0,
            'reasons': all_reasons,
            'headline_pass': headline_result['pass'],
            'body_pass': body_result['pass']
        }
    
    def get_policy_summary(self, retailer_id: str) -> Dict:
        """Get policy summary for retailer."""
        return self.policies.get(retailer_id.lower(), {})
