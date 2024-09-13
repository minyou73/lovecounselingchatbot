import random

class Person:
    def __init__(self, gender, interests):
        self.gender = gender
        self.interests = interests

    def respond_to(self, topic):
        if topic in self.interests:
            return f"I love {topic}! It's one of my favorite things."
        else:
            return f"I don't know much about {topic}, but I'm open to learning more."

class DatingSimulation:
    def __init__(self, male, female):
        self.male = male
        self.female = female
        self.topics = ["movies", "music", "sports", "travel", "food", "books", "art", "technology"]
        self.compatibility_score = 0

    def run_conversation(self, num_exchanges):
        for _ in range(num_exchanges):
            topic = random.choice(self.topics)
            male_response = self.male.respond_to(topic)
            female_response = self.female.respond_to(topic)
            
            print(f"Topic: {topic}")
            print(f"Male: {male_response}")
            print(f"Female: {female_response}")
            print()

            self.calculate_compatibility(topic, male_response, female_response)

    def calculate_compatibility(self, topic, male_response, female_response):
        if "love" in male_response and "love" in female_response:
            self.compatibility_score += 2
        elif "love" in male_response or "love" in female_response:
            self.compatibility_score += 1
        
        if "open to learning" in male_response and "open to learning" in female_response:
            self.compatibility_score += 1

    def get_compatibility_percentage(self):
        max_score = 3 * len(self.topics)  # Maximum possible score
        return (self.compatibility_score / max_score) * 100

# 샘플 데이터
male_interests = ["movies", "sports", "technology", "food"]
female_interests = ["music", "art", "travel", "food"]

male = Person("male", male_interests)
female = Person("female", female_interests)

simulation = DatingSimulation(male, female)
simulation.run_conversation(5)  # 5번의 대화 교환

compatibility = simulation.get_compatibility_percentage()
print(f"Compatibility: {compatibility:.2f}%")