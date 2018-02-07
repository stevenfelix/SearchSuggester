from flask import render_template, request, redirect
from flaskexample import app
from predictions import generate_alternatives
import gensim
import re

path = "flaskexample/models/"
file = 'model_full_50M_sg0_sz250_win5_min3_hs1_neg0' # 50M - no bigram
model = gensim.models.word2vec.Word2Vec.load(path+file)
tags = ['pandas', 'css', 'python']

@app.route('/')
@app.route('/input')
def query_input():
    return render_template("input.html")


@app.route('/output')
def query_output():
  query = request.args.get('query_input')
  
  # send to stack overflow, if requested
  if request.args["to_SO"] == 'True':
      return redirect('https://stackoverflow.com/search?q={}'.format('+'.join(query.split())))
  
  # try to generate alternatives
  try:
      suggestions,synonyms = generate_alternatives(query, 5, model, tags=tags)
  
  # if word submitted does not exist in dictionary, return error
  except Exception as e:
      word = re.search("(?<=\')\w+", str(e)).group()
      message = 'Sorry, \"{}\" is not recognized.'.format(word)
      return render_template("error.html", message=message)
  
  # get number of synonyms to pass for html formatting
  max_l = max([len(l) for l in synonyms])
  
  return render_template("output2.html", suggestions=suggestions, synonyms=synonyms, query=query, max_l=max_l)
    

@app.route('/about')
def about():
    return render_template("about.html")