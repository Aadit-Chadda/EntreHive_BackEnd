from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import uuid

from universities.models import University
from accounts.models import UserProfile
from posts.models import Post
from projects.models import Project
from feed.models import FeedConfiguration


class Command(BaseCommand):
    help = 'Populates the database with realistic users, posts, and projects for feed testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=25,
            help='Number of users to create (default: 25)'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=120,
            help='Number of posts to create (default: 120)'
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=80,
            help='Number of projects to create (default: 80)'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting detailed feed population...")
        
        # Create universities
        universities = self.create_universities()
        self.stdout.write(f"✅ Created {len(universities)} universities")
        
        # Create users
        new_users = self.create_users(universities, options['users'])
        self.stdout.write(f"✅ Created {len(new_users)} users")
        
        # Get all users for content creation
        all_users = list(User.objects.all())
        
        # Create posts
        posts = self.create_posts(all_users, options['posts'])
        self.stdout.write(f"✅ Created {len(posts)} posts")
        
        # Create projects
        projects = self.create_projects(all_users, options['projects'])
        self.stdout.write(f"✅ Created {len(projects)} projects")
        
        # Create feed configurations
        configs = self.create_feed_configurations(all_users)
        self.stdout.write(f"✅ Created {len(configs)} feed configurations")
        
        self.stdout.write(self.style.SUCCESS("🎉 Feed population completed successfully!"))
        self.stdout.write(f"📊 Summary: {len(all_users)} total users, {len(posts)} posts, {len(projects)} projects across {len(universities)} universities")

    def create_universities(self):
        """Create realistic universities"""
        university_data = [
            {
                'name': 'Massachusetts Institute of Technology',
                'short_name': 'MIT',
                'city': 'Cambridge',
                'state_province': 'Massachusetts',
                'country': 'United States',
                'university_type': 'private',
                'website': 'https://mit.edu',
                'email_domain': 'mit.edu'
            },
            {
                'name': 'Stanford University',
                'short_name': 'Stanford',
                'city': 'Stanford',
                'state_province': 'California',
                'country': 'United States',
                'university_type': 'private',
                'website': 'https://stanford.edu',
                'email_domain': 'stanford.edu'
            },
            {
                'name': 'University of California, Berkeley',
                'short_name': 'UC Berkeley',
                'city': 'Berkeley',
                'state_province': 'California',
                'country': 'United States',
                'university_type': 'public',
                'website': 'https://berkeley.edu',
                'email_domain': 'berkeley.edu'
            },
            {
                'name': 'Harvard University',
                'short_name': 'Harvard',
                'city': 'Cambridge',
                'state_province': 'Massachusetts',
                'country': 'United States',
                'university_type': 'private',
                'website': 'https://harvard.edu',
                'email_domain': 'harvard.edu'
            },
            {
                'name': 'California Institute of Technology',
                'short_name': 'Caltech',
                'city': 'Pasadena',
                'state_province': 'California',
                'country': 'United States',
                'university_type': 'private',
                'website': 'https://caltech.edu',
                'email_domain': 'caltech.edu'
            },
            {
                'name': 'Carnegie Mellon University',
                'short_name': 'CMU',
                'city': 'Pittsburgh',
                'state_province': 'Pennsylvania',
                'country': 'United States',
                'university_type': 'private',
                'website': 'https://cmu.edu',
                'email_domain': 'cmu.edu'
            }
        ]
        
        universities = []
        for data in university_data:
            university, created = University.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            universities.append(university)
        
        return universities

    def create_users(self, universities, count):
        """Create realistic users with diverse profiles"""
        
        # Realistic user data
        first_names = [
            'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Avery', 'Riley', 'Cameron',
            'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'William', 'Sophia', 'James',
            'Isabella', 'Benjamin', 'Charlotte', 'Lucas', 'Amelia', 'Mason', 'Mia', 'Ethan',
            'Harper', 'Alexander', 'Evelyn', 'Henry', 'Aria', 'Jacob', 'Luna', 'Michael',
            'Priya', 'Raj', 'Ananya', 'Arjun', 'Sneha', 'Vikram', 'Aditi', 'Karan',
            'Maria', 'Carlos', 'Sofia', 'Diego', 'Valentina', 'Sebastian', 'Camila', 'Mateo'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
            'Patel', 'Sharma', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Jain', 'Verma',
            'Chen', 'Wang', 'Li', 'Zhang', 'Liu', 'Yang', 'Wu', 'Xu'
        ]
        
        industries = ['fintech', 'healthtech', 'edtech', 'cleantech', 'foodtech', 'proptech', 'retailtech', 'agtech', 'spacetech', 'biotech']
        technologies = ['blockchain', 'AI/ML', 'IoT', 'AR/VR', 'quantum computing', 'robotics', 'biotechnology', 'nanotechnology', 'edge computing', '5G']
        fields = ['sustainability', 'healthcare', 'education', 'finance', 'social impact', 'entertainment', 'productivity', 'communication', 'transportation', 'energy']
        
        majors = [
            'Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 
            'Business Administration', 'Economics', 'Psychology', 'Biology', 'Chemistry',
            'Physics', 'Mathematics', 'Data Science', 'Artificial Intelligence',
            'Biomedical Engineering', 'Environmental Science', 'Political Science',
            'International Relations', 'Marketing', 'Finance', 'Philosophy', 'English Literature',
            'Aerospace Engineering', 'Materials Science', 'Neuroscience', 'Pre-Med',
            'Architecture', 'Industrial Design', 'Information Systems', 'Cybersecurity'
        ]
        
        bios = [
            "Passionate about building innovative solutions that make a difference 🚀",
            "Exploring the intersection of technology and human behavior 🧠",
            "Startup enthusiast and future entrepreneur 💡",
            "AI/ML researcher working on next-gen applications 🤖",
            "Sustainable tech advocate and environmental engineer 🌱",
            "Full-stack developer with a love for clean code ⚡",
            "Design thinking enthusiast and UX researcher 🎨",
            "Biotech innovator developing healthcare solutions 🧬",
            "Fintech explorer building the future of finance 💰",
            "Space technology enthusiast and aerospace engineer 🚀",
            "Cybersecurity specialist protecting digital futures 🔐",
            "Social impact entrepreneur solving real-world problems 🌍",
            "Quantum computing researcher pushing boundaries 🔬",
            "Mobile app developer creating seamless experiences 📱",
            "Blockchain developer building decentralized solutions ⛓️",
            "Gaming industry professional and indie game developer 🎮",
            "EdTech innovator revolutionizing education 📚",
            "Hardware engineer bringing ideas to life 🔧",
            "Product manager with a passion for user-centric design 📊",
            "Data scientist uncovering insights from complex datasets 📈"
        ]
        
        users = []
        for i in range(count):
            # Generate username
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=f"{username}@{random.choice(universities).email_domain}",
                first_name=first_name,
                last_name=last_name,
                password='testpass123'
            )
            
            # Create profile
            user_role = random.choice(['student', 'professor', 'investor'])
            profile_defaults = {
                'first_name': first_name,
                'last_name': last_name,
                'user_role': user_role,
                'bio': random.choice(bios),
                'location': f"{random.choice(['San Francisco', 'Boston', 'New York', 'Seattle', 'Austin', 'Chicago'])}, USA",
                'university': random.choice(universities),
            }
            
            # Add role-specific fields
            if user_role == 'student':
                profile_defaults.update({
                    'major': random.choice(majors),
                    'graduation_year': random.randint(2024, 2028)
                })
            elif user_role == 'professor':
                profile_defaults.update({
                    'department': random.choice(['Computer Science', 'Engineering', 'Business', 'Sciences', 'Liberal Arts']),
                    'research_interests': f"Research in {random.choice(fields)} and {random.choice(technologies)}"
                })
            elif user_role == 'investor':
                profile_defaults.update({
                    'investment_focus': f"Early-stage {random.choice(industries)} startups focusing on {random.choice(technologies)}",
                    'company': f"{random.choice(['Venture', 'Capital', 'Innovation', 'Tech', 'Growth'])} {random.choice(['Partners', 'Fund', 'Ventures', 'Capital', 'Labs'])}"
                })
            
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults=profile_defaults
            )
            
            # Ensure the profile has a university (update if needed)
            if not profile.university:
                profile.university = random.choice(universities)
                profile.save()
            
            users.append(user)
        
        return users

    def create_posts(self, users, count):
        """Create diverse and realistic posts"""
        
        # Filter users who have universities
        valid_users = [u for u in users if hasattr(u, 'profile') and u.profile.university]
        if not valid_users:
            self.stdout.write(self.style.WARNING("No users with universities found for posts"))
            return []
        
        # Post content templates
        post_templates = [
            # Startup Ideas
            "🚀 Just had an amazing idea for a {industry} startup! Imagine {concept}. Looking for co-founders who are passionate about {field}. #startup #entrepreneurship #{hashtag}",
            "💡 Working on a revolutionary {product} that could change how we {action}. Early prototype is showing promising results! #innovation #tech #{hashtag}",
            "🎯 Validated my {industry} idea with 50+ potential customers. 89% said they'd pay for this solution! Time to build. #validation #startup #{hashtag}",
            
            # Project Updates
            "📱 Just shipped v2.0 of my {project_type}! New features include {feature1} and {feature2}. Check it out and let me know what you think! #project #development #{hashtag}",
            "🔧 Been working on {project_name} for the past {timeframe}. Finally got {achievement} working! The debugging journey was intense but worth it. #coding #progress #{hashtag}",
            "🎨 Design phase complete for {project_name}! Moving into development next week. Excited to bring this vision to life. #design #ui #{hashtag}",
            
            # Learning & Research
            "📚 Deep diving into {technology} and absolutely loving it! The applications for {use_case} are endless. Any recommended resources? #learning #research #{hashtag}",
            "🧪 Research update: Our {field} study is showing {finding}. This could have major implications for {application}! #research #science #{hashtag}",
            "🤖 Experimenting with {ai_tech} for {purpose}. The results are mind-blowing! AI is truly transforming {industry}. #AI #machinelearning #{hashtag}",
            
            # Networking & Collaboration
            "🤝 Looking for {role} to join our {project_type} team! We're building {description} and need someone with {skills}. DM if interested! #hiring #collaboration #{hashtag}",
            "🎓 Any fellow {major} students working on {field} projects? Would love to connect and share ideas! #networking #collaboration #{hashtag}",
            "💼 Attending {event} next week. Excited to meet fellow entrepreneurs and innovators! Who else is going? #networking #events #{hashtag}",
            
            # Achievements & Milestones
            "🏆 Thrilled to announce that {project_name} won {award} at {competition}! Thank you to my amazing team and everyone who supported us. #achievement #success #{hashtag}",
            "📈 Hit a major milestone today: {metric}! When we started {project_name} {timeframe} ago, this seemed impossible. Persistence pays off! #milestone #growth #{hashtag}",
            "🎉 Just got accepted into {program}! Can't wait to take {project_name} to the next level. The journey continues! #accelerator #startup #{hashtag}",
            
            # Industry Insights
            "📊 The {industry} market is experiencing unprecedented growth. Key trends I'm seeing: {trend1}, {trend2}, and {trend3}. Thoughts? #industry #trends #{hashtag}",
            "🔮 Prediction: {technology} will completely transform {industry} in the next {timeframe}. Here's why... #prediction #future #{hashtag}",
            "💭 Hot take: {controversial_opinion} What do you think? Am I missing something? #opinion #discussion #{hashtag}",
            
            # Personal Journey
            "✨ Reflecting on my {journey_type} journey so far. Key lessons learned: {lesson1}, {lesson2}, and {lesson3}. What would you add? #reflection #growth #{hashtag}",
            "🎯 Setting ambitious goals for {timeframe}: {goal1}, {goal2}, and {goal3}. Accountability partners welcome! #goals #motivation #{hashtag}",
            "📱 Day in the life of a {role}: {activity1}, {activity2}, and {activity3}. Living the dream! #lifestyle #entrepreneur #{hashtag}"
        ]
        
        # Content variables
        industries = ['fintech', 'healthtech', 'edtech', 'cleantech', 'foodtech', 'proptech', 'retailtech', 'agtech', 'spacetech', 'biotech']
        technologies = ['blockchain', 'AI/ML', 'IoT', 'AR/VR', 'quantum computing', 'robotics', 'biotechnology', 'nanotechnology', 'edge computing', '5G']
        fields = ['sustainability', 'healthcare', 'education', 'finance', 'social impact', 'entertainment', 'productivity', 'communication', 'transportation', 'energy']
        hashtags = ['innovation', 'tech', 'startup', 'AI', 'sustainability', 'future', 'disruption', 'growth', 'success', 'building', 'creating', 'developing', 'research', 'science', 'engineering', 'design', 'coding', 'entrepreneurship', 'collaboration', 'networking']
        
        posts = []
        for i in range(count):
            author = random.choice(valid_users)
            template = random.choice(post_templates)
            
            # Fill template with random values
            content = template.format(
                industry=random.choice(industries),
                technology=random.choice(technologies),
                field=random.choice(fields),
                concept=f"a platform that connects {random.choice(['students', 'professionals', 'researchers', 'entrepreneurs'])} with {random.choice(['AI-powered tools', 'sustainable solutions', 'innovative resources', 'collaborative opportunities'])}",
                product=random.choice(['app', 'platform', 'service', 'tool', 'solution', 'system']),
                action=random.choice(['collaborate', 'learn', 'work', 'connect', 'innovate', 'create']),
                project_type=random.choice(['mobile app', 'web platform', 'AI model', 'hardware device', 'research project']),
                project_name=f"{random.choice(['Smart', 'Eco', 'Quantum', 'Neural', 'Green', 'Digital', 'Global', 'Future'])}{random.choice(['Hub', 'Link', 'Flow', 'Sync', 'Core', 'Lab', 'Space', 'Connect'])}",
                feature1=random.choice(['real-time collaboration', 'AI-powered insights', 'advanced analytics', 'seamless integration', 'smart notifications']),
                feature2=random.choice(['dark mode', 'mobile optimization', 'voice commands', 'offline sync', 'customizable dashboard']),
                timeframe=random.choice(['3 months', '6 months', 'a year', '2 years']),
                achievement=random.choice(['the authentication system', 'real-time updates', 'the ML model', 'payment integration', 'the UI framework']),
                use_case=random.choice(['education', 'healthcare', 'finance', 'sustainability', 'social good']),
                purpose=random.choice(['image recognition', 'natural language processing', 'predictive analytics', 'recommendation systems', 'anomaly detection']),
                ai_tech=random.choice(['GPT models', 'computer vision', 'neural networks', 'deep learning', 'transformer models']),
                role=random.choice(['frontend developer', 'backend engineer', 'designer', 'product manager', 'data scientist', 'marketing specialist']),
                description=random.choice(['an AI-powered learning platform', 'a sustainable energy solution', 'a social networking app', 'a productivity tool', 'a healthcare application']),
                skills=random.choice(['React/Node.js experience', 'Python/ML expertise', 'UI/UX design skills', 'iOS/Android development', 'DevOps knowledge']),
                major=random.choice(['CS', 'Engineering', 'Business', 'Design', 'Data Science']),
                award=random.choice(['1st place', 'Best Innovation Award', 'Peoples Choice Award', 'Best Technical Implementation']),
                competition=random.choice(['TechCrunch Disrupt', 'Y Combinator Demo Day', 'MIT Innovation Challenge', 'Stanford TreeHacks', 'Berkeley Hackathon']),
                metric=random.choice(['1000 users', '10K downloads', '$5K revenue', '500 beta signups', '95% user satisfaction']),
                program=random.choice(['Y Combinator', 'Techstars', 'Stanford StartX', 'MIT Delta V', 'Berkeley SkyDeck']),
                trend1=random.choice(['AI integration', 'sustainability focus', 'remote-first approach', 'mobile-first design']),
                trend2=random.choice(['subscription models', 'community building', 'personalization', 'real-time features']),
                trend3=random.choice(['cross-platform compatibility', 'security by design', 'accessibility focus', 'open source adoption']),
                controversial_opinion=random.choice(['remote work is overrated', 'AI will replace most jobs in 10 years', 'crypto is the future of finance', 'social media is harmful for innovation']),
                journey_type=random.choice(['entrepreneurship', 'research', 'development', 'academic', 'career']),
                lesson1=random.choice(['fail fast and iterate', 'user feedback is gold', 'team chemistry matters most', 'focus on one thing well']),
                lesson2=random.choice(['technical debt is real', 'marketing starts on day one', 'networking opens doors', 'persistence beats talent']),
                lesson3=random.choice(['money follows value', 'timing is everything', 'simplicity wins', 'culture eats strategy']),
                goal1=random.choice(['launch my startup', 'publish 3 research papers', 'learn 2 new frameworks', 'build 5 projects']),
                goal2=random.choice(['raise seed funding', 'graduate with honors', 'get 1000 users', 'speak at a conference']),
                goal3=random.choice(['hire a team of 5', 'patent my invention', 'contribute to open source', 'mentor 10 students']),
                activity1=random.choice(['coding sessions', 'user interviews', 'team meetings', 'market research']),
                activity2=random.choice(['prototyping', 'testing features', 'networking events', 'learning new tech']),
                activity3=random.choice(['planning sprints', 'investor pitches', 'customer calls', 'brainstorming sessions']),
                event=random.choice(['TechCrunch Disrupt', 'Web Summit', 'CES', 'SXSW', 'Collision Conference']),
                finding=random.choice(['significant improvement in efficiency', 'unexpected correlation between variables', 'breakthrough in optimization', 'novel approach to the problem']),
                application=random.choice(['renewable energy', 'drug discovery', 'autonomous vehicles', 'personalized medicine', 'climate change']),
                hashtag=random.choice(hashtags)
            )
            
            # Create post (university will be set automatically by the save method)
            post = Post.objects.create(
                author=author,
                content=content,
                visibility=random.choices(
                    ['public', 'university', 'private'],
                    weights=[60, 30, 10]  # More public content for feed diversity
                )[0],
                created_at=timezone.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            posts.append(post)
        
        return posts

    def create_projects(self, users, count):
        """Create diverse and realistic projects"""
        
        # Filter users who have universities
        valid_users = [u for u in users if hasattr(u, 'profile') and u.profile.university]
        if not valid_users:
            self.stdout.write(self.style.WARNING("No users with universities found for projects"))
            return []
        
        # Content variables for projects
        industries = ['fintech', 'healthtech', 'edtech', 'cleantech', 'foodtech', 'proptech', 'retailtech', 'agtech', 'spacetech', 'biotech']
        technologies = ['blockchain', 'AI/ML', 'IoT', 'AR/VR', 'quantum computing', 'robotics', 'biotechnology', 'nanotechnology', 'edge computing', '5G']
        fields = ['sustainability', 'healthcare', 'education', 'finance', 'social impact', 'entertainment', 'productivity', 'communication', 'transportation', 'energy']
        
        # Simple project titles to avoid template errors
        project_titles = [
            # AI/Tech Projects
            "SmartAI", "Neural Network Platform", "Quantum Computing Tool", "AI Assistant",
            "Machine Learning Hub", "Deep Learning Framework", "Computer Vision App", "NLP Processor",
            
            # Sustainability Projects
            "EcoTracker", "Green Energy Monitor", "Sustainable Living App", "Climate Action Platform",
            "Carbon Footprint Calculator", "Renewable Energy Dashboard", "Waste Reduction Tool", "Environmental Impact Tracker",
            
            # Social Impact
            "Social Impact Hub", "Community Builder", "Global Solutions Platform", "Impact Measurement Tool",
            "Change Maker Network", "Unity Platform", "Equality Tech", "Access Bridge",
            
            # Business/Fintech
            "CryptoWallet", "FinTech Platform", "Payment System", "Trading Platform",
            "Investment Tracker", "Budget Buddy", "Wealth Builder", "Market Analyzer",
            
            # Education
            "Learn Fast", "Skill Builder", "Study Sync", "Knowledge Graph",
            "Course Optimizer", "Tutor AI", "Academic Helper", "Research Hub",
            
            # Health/Bio
            "Health Monitor", "Bio Tracker", "Medical Assistant", "Wellness Coach",
            "Fitness Optimizer", "Mental Health App", "Care Connect", "Therapy Bot",
            
            # General Tech
            "Dev Tools", "Code Helper", "Tech Stack Manager", "Cloud Solution",
            "Data Insights", "Security Shield", "Network Optimizer", "System Monitor",
            
            # Startups
            "Next Gen Startup", "Innovation Lab", "Future Tech", "Digital Revolution",
            "Smart Solutions", "Tech Innovator", "Breakthrough Platform", "Disruptive Technology"
        ]
        
        # Simple project descriptions
        description_templates = [
            f"Building the future of {random.choice(industries)} through innovative technology solutions.",
            f"Revolutionary platform leveraging {random.choice(technologies)} to solve real-world problems.",
            f"Open-source project designed for {random.choice(['developers', 'students', 'researchers', 'entrepreneurs'])}.",
            f"Empowering communities through {random.choice(fields)} innovation and sustainable practices.",
            f"Startup working on breakthrough technology to transform {random.choice(industries)}.",
            f"Academic research project exploring {random.choice(technologies)} applications.",
            f"Social impact initiative addressing {random.choice(['climate change', 'education gaps', 'healthcare access', 'digital divide'])}.",
            f"B2B platform helping businesses optimize their {random.choice(['operations', 'customer experience', 'data analytics', 'workflow management'])}."
        ]
        
        projects = []
        for i in range(count):
            owner = random.choice(valid_users)
            
            # Generate project title
            title = random.choice(project_titles)
            
            # Generate description (no template variables)
            description = random.choice(description_templates)
            
            # Create project (university will be set automatically by the save method)
            project = Project.objects.create(
                title=title[:140],  # Ensure it fits within the limit
                owner=owner,
                summary=description,
                project_type=random.choice(['startup', 'side_project', 'research', 'hackathon', 'course_project']),
                status=random.choice(['concept', 'mvp', 'launched']),
                visibility=random.choices(
                    ['public', 'university', 'private'],
                    weights=[50, 35, 15]  # More public/university for feed diversity
                )[0],
                needs=random.sample(['design', 'dev', 'marketing', 'research', 'funding', 'mentor'], k=random.randint(1, 3)),
                created_at=timezone.now() - timedelta(
                    days=random.randint(0, 60),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            
            # Add team members occasionally
            if random.random() > 0.7:  # 30% chance of having team members
                team_size = random.randint(1, 3)
                potential_members = [u for u in valid_users if u != owner and hasattr(u, 'profile') and u.profile.university == owner.profile.university]
                if potential_members:
                    team_members = random.sample(potential_members, min(team_size, len(potential_members)))
                    project.team_members.set(team_members)
            
            projects.append(project)
        
        return projects

    def create_feed_configurations(self, users):
        """Create feed configurations for all users"""
        configs = []
        for user in users:
            config, created = FeedConfiguration.objects.get_or_create(
                user=user,
                defaults={
                    'show_university_posts': random.choice([True, True, True, False]),  # 75% show university
                    'show_public_posts': random.choice([True, True, False]),  # 67% show public
                    'show_project_updates': random.choice([True, True, True, False]),  # 75% show projects
                    'recency_weight': round(random.uniform(0.15, 0.35), 2),
                    'relevance_weight': round(random.uniform(0.15, 0.35), 2),
                    'engagement_weight': round(random.uniform(0.15, 0.35), 2),
                    'university_weight': round(random.uniform(0.15, 0.35), 2),
                }
            )
            
            # Normalize weights to sum to 1.0
            total_weight = config.recency_weight + config.relevance_weight + config.engagement_weight + config.university_weight
            config.recency_weight = round(config.recency_weight / total_weight, 2)
            config.relevance_weight = round(config.relevance_weight / total_weight, 2)
            config.engagement_weight = round(config.engagement_weight / total_weight, 2)
            config.university_weight = round(1.0 - config.recency_weight - config.relevance_weight - config.engagement_weight, 2)
            config.save()
            
            configs.append(config)
        
        return configs
