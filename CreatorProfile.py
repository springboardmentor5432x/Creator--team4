class CreatorProfile:
    def __init__(self, creator_id, name, email, bio):
        self.creator_id = creator_id
        self.name = name
        self.email = email
        self.bio = bio
        self.skills = []

    def update_bio(self, new_bio):
        self.bio = new_bio
        return "Bio updated successfully."

    def add_skill(self, skill):
        if skill not in self.skills:
            self.skills.append(skill)
            return f"Skill '{skill}' added."
        return "Skill already exists."

    def display_profile(self):
        return {
            "ID": self.creator_id,
            "Name": self.name,
            "Email": self.email,
            "Bio": self.bio,
            "Skills": self.skills
        }

# Example Usage
if __name__ == "__main__":
    creator = CreatorProfile("INF001", "Alex Jones", "alex@infosys.com", "Content Creator")
    creator.add_skill("Python")
    creator.add_skill("Git")
    print(creator.display_profile())
