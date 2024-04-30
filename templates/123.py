
from flask import Flask, render_template

app = Flask(__name__)
work_list1 = [
      "инженер-исследователь",
      "пилот",
      "строитель",
      "экзобиолог",
      "врач",
      "инженер по терраформированию",
      "климатолог",
      "специалист по радиационной защите",
      "астрогеолог",
      "гляциолог",
      "инженер жизнеобеспечения",
      "метеоролог",
      "оператор марсохода",
      "киберинженер",
      "штурман",
      "пилот дронов"
    ]

@app.route('/training/<prof>')
def index(prof):
    return render_template('index.html', prof=prof)



@app.route('/list_prof/<olul>')
def work_list(olul):
    return render_template('work_list.html', work_list1=work_list1, ch=olul)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')