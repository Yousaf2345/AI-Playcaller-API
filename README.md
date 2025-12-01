# AI Playcaller API (v2)

## Local dev

1. Create virtual environment & activate:
   - Windows (Powershell):
     ```
     py -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - mac / linux:
     ```
     python -m venv .venv
     source .venv/bin/activate
     ```

2. Install dependencies:
pip install -r requirements.txt

3. Create `.env` from `.env.example` and set SECRET_KEY.

4. Add your model .pkl files to `models/` (use Git LFS if pushing to GitHub).

5. Run: uvicorn app.main:app --reload


6. Test:
- Offensive:
  ```
  curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" -d "{\"down\":3,\"ydstogo\":5,\"yrdline100\":60,\"qtr\":2,\"ScoreDiff\":-3}"
  ```
- Defensive:
  ```
  curl -X POST "http://127.0.0.1:8000/predict_defense" -H "Content-Type: application/json" -d "{\"down\":3,\"ydstogo\":5,\"yardline_100\":60,\"qtr\":2,\"score_differential\":-3,\"quarter_seconds_remaining\":900}"
  ```

7. Create account: curl -X POST "http://127.0.0.1:8000/auth/signup
" -H "Content-Type: application/json" -d "{"username":"coach1","email":"a@b.com
","password":"pass","full_name":"Coach One","is_admin":true}"


## Deploying to Render

- Make sure model pickles are in `models/`. Use Git LFS to track large files:

git lfs install
git lfs track ".pkl"
git add .gitattributes
git add models/.pkl
git commit -m "Add models"
git push

- Use Render Web Service with `uvicorn app.main:app --host 0.0.0.0 --port $PORT` as start command.
- Provide environment vars in Render UI (SECRET_KEY etc).



