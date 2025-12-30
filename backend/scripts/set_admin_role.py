"""
Admin Role Management Script

Utility script to set or remove admin custom claims for users.
Run this script to grant admin privileges to users.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.firebase_config import initialize_firebase, get_auth, get_db


def set_admin_role(email: str, is_admin: bool = True):
    """
    Set or remove admin role for a user by email.
    
    Args:
        email: User's email address
        is_admin: True to grant admin, False to remove admin
    """
    try:
        # Initialize Firebase
        initialize_firebase()
        auth = get_auth()
        
        # Get user by email
        user = auth.get_user_by_email(email)
        
        # Set custom claims
        auth.set_custom_user_claims(user.uid, {'admin': is_admin})
        
        action = "granted" if is_admin else "revoked"
        print(f"✓ Admin privileges {action} for user: {email}")
        print(f"  User ID: {user.uid}")
        print(f"  Display Name: {user.display_name}")
        
        # Verify the claims were set
        updated_user = auth.get_user(user.uid)
        print(f"  Custom Claims: {updated_user.custom_claims}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error setting admin role: {str(e)}")
        return False


def list_admins():
    """List all users with admin privileges."""
    try:
        # Initialize Firebase
        initialize_firebase()
        auth = get_auth()
        
        print("\n=== Current Admin Users ===")
        
        admins_found = 0
        page = auth.list_users()
        
        for user in page.users:
            if user.custom_claims and user.custom_claims.get('admin'):
                admins_found += 1
                print(f"\n{admins_found}. Email: {user.email}")
                print(f"   UID: {user.uid}")
                print(f"   Name: {user.display_name}")
                print(f"   Disabled: {user.disabled}")
        
        while page.has_next_page:
            page = page.get_next_page()
            for user in page.users:
                if user.custom_claims and user.custom_claims.get('admin'):
                    admins_found += 1
                    print(f"\n{admins_found}. Email: {user.email}")
                    print(f"   UID: {user.uid}")
                    print(f"   Name: {user.display_name}")
                    print(f"   Disabled: {user.disabled}")
        
        if admins_found == 0:
            print("No admin users found.")
        else:
            print(f"\nTotal admins: {admins_found}")
        
        return admins_found
        
    except Exception as e:
        print(f"✗ Error listing admins: {str(e)}")
        return 0


def verify_admin_status(email: str):
    """Check if a user has admin privileges."""
    try:
        # Initialize Firebase
        initialize_firebase()
        auth = get_auth()
        
        user = auth.get_user_by_email(email)
        
        print(f"\n=== User Status ===")
        print(f"Email: {user.email}")
        print(f"UID: {user.uid}")
        print(f"Name: {user.display_name}")
        print(f"Disabled: {user.disabled}")
        print(f"Custom Claims: {user.custom_claims}")
        
        is_admin = user.custom_claims and user.custom_claims.get('admin', False)
        print(f"\n{'✓' if is_admin else '✗'} Admin Status: {is_admin}")
        
        return is_admin
        
    except Exception as e:
        print(f"✗ Error checking admin status: {str(e)}")
        return False


def main():
    """Main function with interactive menu."""
    load_dotenv()
    
    print("=" * 60)
    print("Admin Role Management Tool")
    print("=" * 60)
    
    while True:
        print("\n\nOptions:")
        print("1. Grant admin privileges to user")
        print("2. Revoke admin privileges from user")
        print("3. List all admin users")
        print("4. Check user admin status")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            email = input("Enter user email: ").strip()
            if email:
                set_admin_role(email, is_admin=True)
            else:
                print("✗ Email cannot be empty")
        
        elif choice == "2":
            email = input("Enter user email: ").strip()
            if email:
                confirm = input(f"Are you sure you want to revoke admin for {email}? (yes/no): ").strip().lower()
                if confirm == "yes":
                    set_admin_role(email, is_admin=False)
                else:
                    print("Operation cancelled")
            else:
                print("✗ Email cannot be empty")
        
        elif choice == "3":
            list_admins()
        
        elif choice == "4":
            email = input("Enter user email: ").strip()
            if email:
                verify_admin_status(email)
            else:
                print("✗ Email cannot be empty")
        
        elif choice == "5":
            print("\nGoodbye!")
            break
        
        else:
            print("✗ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
