import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE')
        return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
        categories = {
            category.id: category.type for category in Category.query.all()
        }
        return jsonify({
            'categories': categories,
            'Available_categories': len(categories)
        })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route("/questions", methods=["GET"])
  def get_questions():
      page = request.args.get("page", 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = list(map(Question.format, Question.query.all()))
      current_questions = paginate_questions(request, questions)

      if (len(questions) == 0):
          abort(404)

      total_questions = len(questions)
      questions = questions[start:end]

      categories = get_all_categories().get_json()["categories"]

      result = {
          "questions": questions,
          "total_questions": total_questions,
          "current_category": None,
          "categories": categories,
      }
      return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def delete_question(q_id):
      try:
          question = Question.query.get(question_id)

          if question is None:
              abort(404)
              
          question.delete()
          return jsonify({
            'success': True,
            'message': "Question successfully deleted",
            'delete_id': q_id,
            'questions': questions
          })
      except Exception:
          abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def question_add():
    question = data.get('question')
    answer = data.get('answer')
    difficulty = data.get('difficulty')
    category = data.get('category')

    if ((question == '') or (answer == '') or
                (difficulty == '') or (category == '')):
            abort(400)

    category = Category.query.filter(Category.id == category).one_or_none()
        if category is None:
            abort(400)
    try:
        new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
        Question.insert(new_question)
        return jsonify(new_question.format())
    except Exception:
        abort(500)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def question_search():
    criteria = request.get_json()['searchTerm']

    if criteria == '':
        abort(404)
    try:
        search_result = Question.query.filter(Question.question.ilike(f'%{criteria}%')).all()
        data = [question.format() for question in search_result]
        return jsonify({"questions": data, 
                        "questions_count": len(data)
        })
    except Exception:
        abort(404)
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def find_by_category(cat_id):
      category = Category.query.filter(Category.id == cat_id).one_or_none()
      if category is None:
          abort(404)
     
      try:
          questions = [question.format() for question in Question.query.filter(
            Question.category_id == category.id).all()]
          return jsonify({
              'questions': questions,
              'questions_count': len(questions),
              'category_id': id
          })
      except Exception:
          abort(404)
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz_play():
      data = request.get_json()
      previous_questions = data['previous_questions']
      quiz_category = data['quiz_category']
      category_id = int(quiz_category['id'])
      if quiz_category is None:
          abort(400)
      if previous_questions is None:
          abort(400)
      try:
        
        if category_id == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
                    category=category_id).all()
      
        if len(questions) > 0:
          filtered_questions = [question.format() for question in questions if question.id not in previous_questions]
        
          if len(filtered_questions) > 0:
            new_question = random.choice(filtered_questions)
          else:
            new_question = None
          return jsonify({
            'success': True,
            'question': new_question,
            'previous_questions': previous_questions,
            'quizCategory': quiz_category
          })
        else:
          return jsonify({"question": None})
      except Exception:
          abort(500)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def data_not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Data Not Found"
      }), 404

  @app.errorhandler(422)
  def data_not_processable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Data Not processable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
      }), 400     
  
  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Server Error or Iternal Error"
      }), 500     

  return app

    