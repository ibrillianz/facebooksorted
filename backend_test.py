
import requests
import unittest
import sys
import json
from datetime import datetime

class NeurodivergentOrganizerAPITest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://d480c7e2-e1c5-47c8-8246-6651cb63cf13.preview.emergentagent.com"
        self.test_content_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def setUp(self):
        self.tests_run += 1

    def tearDown(self):
        if hasattr(self, '_outcome'):
            result = self.defaultTestResult()
            self._feedErrorsToResult(result, self._outcome.errors)
            if result.wasSuccessful():
                self.tests_passed += 1

    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing health check endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["service"], "Neurodivergent Content Organizer")
            print("✅ Health check passed")
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            raise

    def test_02_add_content(self):
        """Test adding new content"""
        print("\n🔍 Testing add content endpoint...")
        
        try:
            # Use a public Facebook post URL
            test_url = "https://www.facebook.com/Meta/posts/pfbid02Ld9JQtTdHcGJEZzXbQUkKcGBWTzJSWkUYZVYBvnHXcUNkGZJC9qZKFJgRMJg7Fwl"
            
            payload = {
                "url": test_url,
                "tags": ["test", "api"],
                "category": "Education"
            }
            
            response = requests.post(
                f"{self.base_url}/api/content",
                json=payload
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["url"], test_url)
            self.assertEqual(data["category"], "Education")
            self.assertListEqual(data["tags"], ["test", "api"])
            self.assertIsNotNone(data["id"])
            
            # Save the content ID for later tests
            self.test_content_id = data["id"]
            print(f"✅ Content added successfully with ID: {self.test_content_id}")
        except Exception as e:
            print(f"❌ Add content failed: {str(e)}")
            raise

    def test_03_get_all_content(self):
        """Test getting all content"""
        print("\n🔍 Testing get all content endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/content")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            
            # Check if our test content is in the list
            if self.test_content_id:
                found = False
                for item in data:
                    if item["id"] == self.test_content_id:
                        found = True
                        break
                self.assertTrue(found, "Added test content not found in content list")
            
            print(f"✅ Retrieved {len(data)} content items successfully")
        except Exception as e:
            print(f"❌ Get all content failed: {str(e)}")
            raise

    def test_04_search_content(self):
        """Test searching content"""
        print("\n🔍 Testing search content endpoint...")
        
        try:
            # Search for the test tag we added
            payload = {
                "query": "test"
            }
            
            response = requests.post(
                f"{self.base_url}/api/search",
                json=payload
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            
            # Check if our test content is in the search results
            if self.test_content_id and len(data) > 0:
                found = False
                for item in data:
                    if item["id"] == self.test_content_id:
                        found = True
                        break
                self.assertTrue(found, "Added test content not found in search results")
            
            print(f"✅ Search returned {len(data)} results successfully")
        except Exception as e:
            print(f"❌ Search content failed: {str(e)}")
            raise

    def test_05_get_categories(self):
        """Test getting categories"""
        print("\n🔍 Testing get categories endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/categories")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            
            # Check if our test category is in the list
            if len(data) > 0:
                categories = [cat["name"] for cat in data]
                print(f"Available categories: {', '.join(categories)}")
                
                # Our test content had "Education" category
                self.assertIn("Education", categories, "Test category not found in categories list")
            
            print(f"✅ Retrieved {len(data)} categories successfully")
        except Exception as e:
            print(f"❌ Get categories failed: {str(e)}")
            raise

    def test_06_get_tags(self):
        """Test getting tags"""
        print("\n🔍 Testing get tags endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            
            # Check if our test tags are in the list
            if len(data) > 0:
                tags = [tag["name"] for tag in data]
                print(f"Available tags: {', '.join(tags)}")
                
                # Our test content had "test" and "api" tags
                self.assertTrue(
                    "test" in tags or "api" in tags, 
                    "None of the test tags found in tags list"
                )
            
            print(f"✅ Retrieved {len(data)} tags successfully")
        except Exception as e:
            print(f"❌ Get tags failed: {str(e)}")
            raise

    def test_07_delete_content(self):
        """Test deleting content"""
        print("\n🔍 Testing delete content endpoint...")
        
        if not self.test_content_id:
            self.skipTest("No test content ID available to delete")
        
        try:
            response = requests.delete(f"{self.base_url}/api/content/{self.test_content_id}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["message"], "Content deleted successfully")
            
            # Verify it's deleted by trying to find it in all content
            response = requests.get(f"{self.base_url}/api/content")
            all_content = response.json()
            
            found = False
            for item in all_content:
                if item["id"] == self.test_content_id:
                    found = True
                    break
            
            self.assertFalse(found, "Content was not actually deleted")
            print(f"✅ Content with ID {self.test_content_id} deleted successfully")
        except Exception as e:
            print(f"❌ Delete content failed: {str(e)}")
            raise

def run_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(NeurodivergentOrganizerAPITest))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    test_instance = NeurodivergentOrganizerAPITest()
    print(f"\n📊 Tests passed: {test_instance.tests_passed}/{test_instance.tests_run}")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
