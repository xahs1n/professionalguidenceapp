import os
import django
from django.test.client import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'p2p.settings')
django.setup()

from django.contrib.auth import get_user_model
from home.models import Session, DirectMessage

User = get_user_model()

def run_tests():
    print("--- Starting Backend Tests ---")
    
    mentee = User.objects.filter(username='mentee').first()
    mentor = User.objects.filter(username='mentor').first()

    if not mentee or not mentor:
         print("ERROR: User 'mentee' or 'mentor' not found in database. Using admin.")
         admin = User.objects.filter(username='admin').first()
         # fallback assigning roles
         if not mentor:
             mentor, _ = User.objects.get_or_create(username='mentor', email='mentor@m.com')
             mentor.set_password('shary123')
             mentor.user_type = 'mentor'
             mentor.save()
         if not mentee:
             mentee = admin
    
    # Give them overlapping tags
    mentee.skills.add('React', 'Python')
    mentor.skills.add('React', 'Python')
    mentor.is_available_for_mentoring = True
    mentor.save()
    mentee.save()

    print("1. Testing Matching System...")
    c = Client()
    c.force_login(mentee)
    
    response = c.get('/sessions/browse/')
    if response.status_code == 200:
        recommended = response.context.get('recommended_mentors')
        if recommended is not None and mentor in recommended:
            print(" SUCCESS: Matching system works logically! Mentor found via Tag matching.")
        else:
            print(" FAILED: Mentor not in recommended_mentors. Debug: Check user context or tags.")
    else:
        print(f" FAILED: Browse sessions returned status code: {response.status_code}")

    print("2. Testing Chat Messaging...")
    DirectMessage.objects.create(sender=mentee, recipient=mentor, content="Hello! This is a test message to ensure DB connects properly.")
    
    chat_response = c.get('/chat/')
    if chat_response.status_code == 200:
        threads = chat_response.context.get('threads', [])
        if any(t['other_user'] == mentor for t in threads):
            print(" SUCCESS: Chat threading logic works. Thread with mentor found in Inbox.")
        else:
            print(" FAILED: Thread not generated in chat_inbox.")
    else:
         print(f" FAILED: Chat inbox returned status code: {chat_response.status_code}")

    # Test Chat Room
    chat_room_resp = c.get(f'/chat/{mentor.id}/')
    if chat_room_resp.status_code == 200:
        messages = chat_room_resp.context.get('chat_messages')
        if messages and messages.count() > 0:
            print(" SUCCESS: Chat room correctly loads historical messages.")
        else:
            print(" FAILED: Historical messages missing from room context.")
            
    print("--- Tests Completed! ---")

if __name__ == '__main__':
    run_tests()
