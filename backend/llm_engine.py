from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities import SerpAPIWrapper
from chatbot_safety_module import WomenFocusedChatbotSafety
from guardrails import Guard
from job_fetcher import get_jobs_by_keyword,fetch_herkey_featured_events_safari

class LLMResponder:
    def __init__(self, vector_store):
        self.guard = Guard.from_rail("asha_guard.rail")
        self.vector_store = vector_store
        self.gemini_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        self.search = SerpAPIWrapper(params={"engine": "bing", "gl": "us", "hl": "en"})
        self.safety_filter = WomenFocusedChatbotSafety()
        
        keyword_prompt = PromptTemplate(
            input_variables=["user_query"],
            template="""Extract the most relevant simple job or event keyword from the user's input below. 
        Only output the single keyword like "java", "python", "data analyst", "frontend", "backend", etc.
        No extra words or sentences.

        User Input: {user_query}
        Keyword:"""
        )
        self.keyword_extractor_chain = LLMChain(llm=self.gemini_model, prompt=keyword_prompt)

        DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and a Career Advisor. The Advisor guides the user regarding jobs, interests, upcoming job events, workshops, bootcamp and domain selection decisions.
        It follows the previous conversation to do so.

        Relevant pieces of previous conversation:
        {context},

        Useful information from career guidance books:
        {text},

        Useful information about career guidance from Web:
        {web_knowledge},

        Upcoming relevant career events or bootcamps:
        {events_data},

        About jobs:
        {jobs_info},

        Current conversation:
        Human: {input}
        Career Expert:
"""

        self.template = PromptTemplate(
            input_variables=["context", "input", "text", "web_knowledge","events_data","jobs_info"],
            template=DEFAULT_TEMPLATE
        )
        self.chain = LLMChain(llm=self.gemini_model, prompt=self.template)

    def load_fallback_message(self):
        with open("asha_fallback_response.md", "r", encoding="utf-8") as f:
            return f.read()

    def generate_response(self, message, history):
        docs = self.vector_store.similarity_search(message)

        # 🔥 Safe web search
        try:
            web_knowledge = self.search.run(message)
        except Exception as e:
            print(f"⚠️ Web search failed via SerpAPI: {str(e)}")
            web_knowledge = "No relevant web knowledge found."

        # 🔥 Extract job/event keyword
        try:
            clean_keyword = self.keyword_extractor_chain.predict(user_query=message).strip().lower()
            print(f"🎯 Cleaned keyword extracted from LLM: {clean_keyword}")
        except Exception as e:
            print(f"⚠️ Failed to extract keyword: {str(e)}")
            clean_keyword = ""

        jobs_info = ""
        events_data = ""

        job_detection_prompt = PromptTemplate(
        input_variables=["user_query"],
        template="""Determine if the user's query is primarily about finding job openings, applying for jobs, or exploring employment opportunities. 
If the query is about salary, salary comparison, platform comparison, or confidential topics, respond "no".
        Respond ONLY with "yes" or "no" (no extra text).

        User Input: {user_query}
        Answer:"""
        )

        self.job_detector_chain = LLMChain(llm=self.gemini_model, prompt=job_detection_prompt)
        is_job_related = self.job_detector_chain.predict(user_query=message).strip().lower()
        print(f"🎯 is_job_related extracted from LLM: {is_job_related}")

        if is_job_related == "yes":

        # 🔥 Fetch jobs
        #if "job" in message.lower() or "apply" in message.lower():
            try:
                print("🔄 Trying to fetch jobs info...")
                jobs = get_jobs_by_keyword(clean_keyword)
                if jobs:
                    jobs_info = "\n\n".join([
                        f"🔹 **{job['title']}** at {job['company']} ({job['location']})"
                        for job in jobs[:3]
                    ])
                else:
                    jobs_info = "No latest jobs found at the moment. Please check [HerKey jobs](https://www.herkey.com/jobs) directly."
            except Exception as e:
                print(f"⚠️ Failed to fetch jobs: {str(e)}")
                jobs_info = "Unable to fetch job listings due to server issues. Please check [HerKey jobs](https://www.herkey.com/jobs)."

        # 🔥 Fetch events
        event_keywords = ["event", "bootcamp", "workshop", "career fair", "networking"]
        if any(kw in message.lower() for kw in event_keywords):
            try:
                print("🔄 Trying to fetch featured events...")
                events = fetch_herkey_featured_events_safari()
                if events:
                    events_data = "\n\n".join([
                        f"🔹 [{ev['name']}]({ev['link']})" for ev in events[:5]
                    ])
                else:
                    events_data = "No upcoming featured events found on HerKey right now."
            except Exception as e:
                print(f"⚠️ Failed to fetch events: {str(e)}")
                events_data = "Unable to fetch event details. Please check [HerKey Events](https://events.herkey.com/)."

        # 🔥 Final LLM output
        try:
            raw_response = self.chain.predict(
                context=history,
                input=message,
                text=docs,
                web_knowledge=web_knowledge,
                jobs_info=jobs_info,
                events_data=events_data
            )
        except Exception as e:
            print(f"⚠️ LLM chain failed to generate response: {str(e)}")
            raw_response = ""

        # 🔥 Post-process output safely
        if raw_response and "Career Expert:" in raw_response:
            extracted_response = raw_response.split("Career Expert:", 1)[-1].strip()
        elif raw_response:
            extracted_response = raw_response.strip()
        else:
            print("⚠️ Empty raw response received from LLM.")
            extracted_response = "I'm here to assist you! Could you please rephrase or ask your query again?"

        print(f"📝 Extracted response: {extracted_response}")

        # 🔥 Apply safety filter
        safe_result = self.safety_filter.process_message(message, extracted_response)
        filtered_response = safe_result["final_response"]

        # 🔥 Prepare final sections
        conversation_reply = filtered_response
        jobs_reply = ""
        events_reply = ""

        if jobs_info and "Unable to fetch" not in jobs_info:
            jobs_reply = f"Here are some {clean_keyword} job opportunities I found for you:\n\n"
            jobs_reply += jobs_info
            jobs_reply += "\n\n[🔗 View More Jobs on HerKey](https://www.herkey.com/jobs)"

        if events_data and "Unable to fetch" not in events_data:
            events_reply = "\n\nHere are some featured events happening soon:\n\n"
            events_reply += events_data
            events_reply += "\n\n[🔗 View More Events on HerKey](https://events.herkey.com/)"

        print("--------------------" + events_reply)

        # 🔥 Guardrails Validation
        try:
            validation_output = self.guard.validate(llm_output=conversation_reply)
            print(validation_output)
            print("✅ Guardrails validation success.")

            if validation_output.validated_output:
                conversation_reply = validation_output.validated_output.get("response", self.load_fallback_message())

            return {
                "conversation": conversation_reply,
                "jobs": jobs_reply,
                "events": events_reply
            }

        except Exception as e:
            print(f"⚠️ Guardrails validation failed: {str(e)}")
            return {
                "conversation": self.load_fallback_message(),
                "jobs": jobs_reply,
                "events": events_reply
            }
