import google.generativeai as genai

genai.configure(api_key="AIzaSyDVc2Y_MB-p8CEA06x6IsKPwrkHy0dUd7I")

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Hello")

print(response.text)