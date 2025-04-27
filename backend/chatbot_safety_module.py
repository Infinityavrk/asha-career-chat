import re
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

class GenderBiasMitigation:
    """
    A class to detect and mitigate gender bias in language model outputs.
    """
    
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # Define gender word pairs for bias detection
        self.gender_pairs = [
            ("he", "she"), ("him", "her"), ("his", "hers"), 
            ("man", "woman"), ("men", "women"),
            ("boy", "girl"), ("boys", "girls"),
            ("male", "female"), ("father", "mother"),
            ("husband", "wife"), ("son", "daughter")
        ]
        
        # Define stereotypical profession associations to flag
        self.stereotypical_associations = {
            "masculine_coded": ["engineer", "doctor", "scientist", "programmer", "CEO", "analyst"],
            "feminine_coded": ["nurse", "teacher", "assistant", "secretary", "homemaker"]
        }
        
        # Load gender direction in embedding space (simplified version)
        # In production, use a more sophisticated approach for the gender direction
        self.gender_direction = self._compute_gender_direction()
    
    def _compute_gender_direction(self):
        """Compute gender direction in embedding space using gendered word pairs."""
        gender_vectors = []
        
        for male, female in self.gender_pairs:
            male_ids = self.tokenizer.encode(male, return_tensors="pt")
            female_ids = self.tokenizer.encode(female, return_tensors="pt")
            
            with torch.no_grad():
                male_embedding = self.model(male_ids).last_hidden_state.mean(dim=1)
                female_embedding = self.model(female_ids).last_hidden_state.mean(dim=1)
            
            gender_vectors.append((male_embedding - female_embedding).squeeze().numpy())
        
        # Average the gender directions
        return np.mean(gender_vectors, axis=0)
    
    def detect_gender_bias(self, text):
        """
        Detects potential gender bias in text.
        Returns a dict with bias scores and flagged issues.
        """
        results = {
            "bias_score": 0.0,
            "stereotypical_associations": [],
            "gendered_language": [],
            "needs_review": False
        }
        
        # Check for stereotypical associations
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in self.stereotypical_associations["masculine_coded"]:
                results["stereotypical_associations"].append(f"Masculine-coded term: {word}")
                results["bias_score"] += 0.2
            
            if word in self.stereotypical_associations["feminine_coded"]:
                results["stereotypical_associations"].append(f"Feminine-coded term: {word}")
                results["bias_score"] += 0.2
        
        # Check for gendered language when unnecessary
        for male, female in self.gender_pairs:
            if male in words and female not in text.lower():
                results["gendered_language"].append(f"Potentially unnecessary gendered term: {male}")
                results["bias_score"] += 0.15
        
        # Flag for review if bias score exceeds threshold
        if results["bias_score"] > 0.5:
            results["needs_review"] = True
            
        return results
    
    def mitigate_gender_bias(self, text):
        """
        Attempts to mitigate gender bias in the provided text.
        Returns modified text with reduced bias.
        """
        # Replace masculine default with gender-neutral options
        text = re.sub(r'\b(?:mankind|man-made)\b', 'humanity|artificial', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:businessman|businessmen)\b', 'business professional(s)', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:fireman|firemen)\b', 'firefighter(s)', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:policeman|policemen)\b', 'police officer(s)', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:chairman|chairmen)\b', 'chairperson|chair', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhe or she\b', 'they', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhis or hers?\b', 'theirs', text, flags=re.IGNORECASE)
        
        # For more sophisticated debiasing, you would project embeddings 
        # away from the gender direction before generating text
        
        return text


class SafetyGuardrails:
    """
    Implements safety guardrails for a women-focused chatbot.
    """
    
    def __init__(self):
        # Define sensitive topics that need careful handling
        self.sensitive_topics = [
            "sexual assault", "rape", "domestic violence", "abuse", 
            "harassment", "eating disorder", "self-harm", "suicide",
            "abortion", "miscarriage", "fertility", "pregnancy loss"
        ]
        
        # Crisis resources to provide when needed
        self.crisis_resources = {
            "domestic_violence": "National Domestic Violence Hotline: 1-800-799-7233",
            "sexual_assault": "RAINN: 1-800-656-HOPE (4673)",
            "mental_health": "Crisis Text Line: Text HOME to 741741",
            "suicide": "National Suicide Prevention Lifeline: 1-800-273-8255",
            "general": "If you're experiencing an emergency, please call 911 or your local emergency number."
        }
        
        # Privacy-sensitive topics
        self.privacy_sensitive = [
            "medical", "health", "menstruation", "gynecological", 
            "reproductive", "pregnancy", "birth control"
        ]
    
    def check_content(self, user_input, response_text):
        """
        Checks both user input and potential response for safety issues.
        Returns dict with safety flags and any needed resources.
        """
        results = {
            "sensitive_topics_detected": [],
            "privacy_warning_needed": False,
            "crisis_resources": [],
            "content_warning_needed": False,
            "modified_response": response_text
        }
        
        combined_text = (user_input + " " + response_text).lower()
        
        # Check for sensitive topics
        for topic in self.sensitive_topics:
            if topic in combined_text:
                results["sensitive_topics_detected"].append(topic)
                results["content_warning_needed"] = True
                
                # Add appropriate crisis resources
                if topic in ["sexual assault", "rape"]:
                    results["crisis_resources"].append(self.crisis_resources["sexual_assault"])
                elif topic in ["domestic violence", "abuse"]:
                    results["crisis_resources"].append(self.crisis_resources["domestic_violence"])
                elif topic in ["self-harm", "suicide"]:
                    results["crisis_resources"].append(self.crisis_resources["suicide"])
                elif topic in ["eating disorder"]:
                    results["crisis_resources"].append(self.crisis_resources["mental_health"])
        
        # Check for privacy-sensitive topics
        for topic in self.privacy_sensitive:
            if topic in combined_text:
                results["privacy_warning_needed"] = True
                break
        
        # Add privacy disclaimer if needed
        if results["privacy_warning_needed"]:
            privacy_note = ("\n\nPlease note: This chatbot is not a substitute for professional medical advice, "
                           "and our conversation is not protected by medical privacy laws. "
                           "For health concerns, please consult with a healthcare provider.")
            results["modified_response"] += privacy_note
        
        # Add crisis resources if needed
        if results["crisis_resources"]:
            resources_text = "\n\nSupport resources:\n" + "\n".join(results["crisis_resources"])
            results["modified_response"] += resources_text
        
        return results


class InclusiveLanguageChecker:
    """
    Checks for and suggests more inclusive language options.
    """
    
    def __init__(self):
        # Dictionary of non-inclusive terms and suggested alternatives
        self.term_alternatives = {
            # Body size terms
            "overweight": ["higher weight", "larger body"],
            "obese": ["person with obesity", "higher weight"],
            "fat": ["higher weight", "larger body"],
            
            # Medical terms
            "diabetic": ["person with diabetes", "person living with diabetes"],
            "handicapped": ["person with a disability", "person with mobility needs"],
            "disabled": ["person with a disability", "person with accessibility needs"],
            
            # Othering language
            "normal women": ["typically developing women", "women without [specific condition]"],
            "normal body": ["typical body", "average body"],
            
            # Gendered terms that exclude some women
            "pregnant women": ["pregnant people", "people who are pregnant"],
            "breastfeeding": ["chestfeeding", "nursing", "feeding"],
            
            # Mental health
            "crazy": ["concerning", "unusual"],
            "insane": ["extreme", "extraordinary"],
            
            # Age-related
            "elderly women": ["older women", "women over X age"],
            "girls": ["women", "adults"] # When referring to adult women
        }
    
    def check_text(self, text):
        """
        Checks text for non-inclusive language and suggests alternatives.
        Returns the original text and a list of suggestions.
        """
        results = {
            "original_text": text,
            "suggestions": []
        }
        
        # Convert to lowercase for checking but keep original for display
        text_lower = text.lower()
        
        for term, alternatives in self.term_alternatives.items():
            if term in text_lower:
                suggestion = {
                    "term": term,
                    "alternatives": alternatives,
                    "context": self._get_context(text, term)
                }
                results["suggestions"].append(suggestion)
        
        return results
    
    def _get_context(self, text, term):
        """Extract a snippet of text containing the term for context."""
        # Find the term in the text (case insensitive)
        term_index = text.lower().find(term.lower())
        if term_index == -1:
            return ""
        
        # Get some context before and after (about 40 chars each way)
        start = max(0, term_index - 40)
        end = min(len(text), term_index + len(term) + 40)
        
        context = text[start:end]
        # Add ellipsis if we truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
            
        return context
    
    def suggest_improvements(self, text):
        """
        Suggests an improved version of the text with more inclusive language.
        """
        improved_text = text
        check_results = self.check_text(text)
        
        for suggestion in check_results["suggestions"]:
            term = suggestion["term"]
            # Default to first alternative
            replacement = suggestion["alternatives"][0]
            
            # Case-preserving replacement
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            
            def match_case(match):
                matched_text = match.group(0)
                if matched_text.islower():
                    return replacement.lower()
                elif matched_text.isupper():
                    return replacement.upper()
                elif matched_text[0].isupper():
                    return replacement[0].upper() + replacement[1:]
                return replacement
            
            improved_text = pattern.sub(match_case, improved_text)
            
        return improved_text


# Example of using all components together in a chatbot pipeline
class WomenFocusedChatbotSafety:
    def __init__(self, base_model_name="bert-base-uncased"):
        self.bias_mitigator = GenderBiasMitigation(model_name=base_model_name)
        self.safety_guardrails = SafetyGuardrails()
        self.inclusive_checker = InclusiveLanguageChecker()
        
        # In a real implementation, you would initialize your base chatbot model here
        # self.chatbot_model = load_your_chatbot_model()
    
    def process_message(self, user_input, raw_response):
        """
        Process a user message and chatbot response through all safety systems.
        Returns a safer, more inclusive, and less biased response.
        """
        # Step 1: Check for gender bias in the raw response
        bias_results = self.bias_mitigator.detect_gender_bias(raw_response)
        
        # Step 2: Mitigate any gender bias if score is significant
        processed_response = raw_response
        if bias_results["bias_score"] > 0.3:
            processed_response = self.bias_mitigator.mitigate_gender_bias(raw_response)
        
        # Step 3: Check for inclusive language
        inclusive_check = self.inclusive_checker.check_text(processed_response)
        if inclusive_check["suggestions"]:
            processed_response = self.inclusive_checker.suggest_improvements(processed_response)
        
        # Step 4: Apply safety guardrails
        safety_results = self.safety_guardrails.check_content(user_input, processed_response)
        final_response = safety_results["modified_response"]
        
        # Return both the processed response and the safety/bias analytics
        return {
            "final_response": final_response,
            "bias_analysis": bias_results,
            "safety_analysis": safety_results,
            "inclusive_language_analysis": inclusive_check["suggestions"]
        }


# Example usage
def example_chatbot_interaction():
    # Initialize the safety system
    safety_system = WomenFocusedChatbotSafety()
    
    # Mock chatbot response (in a real system, this would come from your LLM)
    user_message = "I've been experiencing severe depression lately."
    raw_chatbot_response = "Many girls feel down sometimes. You should try to be more positive and not act crazy about it. Normal women can handle these emotions better."
    
    # Process through safety system
    result = safety_system.process_message(user_message, raw_chatbot_response)
    
    print("Original response:")
    print(raw_chatbot_response)
    print("\nFinal safe response:")
    print(result["final_response"])
    print("\nBias analysis:", result["bias_analysis"])
    print("\nInclusive language suggestions:", result["inclusive_language_analysis"])
    
    return result


if __name__ == "__main__":
    example_chatbot_interaction()