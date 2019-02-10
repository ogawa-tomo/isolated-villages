from flask import Flask, render_template, request, redirect, url_for
from setting import Setting
import calc_isolation
import time
from setting import URL
import search_isolated_faculty


app = Flask(__name__)
title = "孤立集落探索アプリケーション"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["GET", "POST"])
def post():
    if request.method == "POST":

        start = time.time()

        region = request.form["region"]
        # population_param = float(request.form["population_param"])
        # distance_param = float(request.form["distance_param"])
        point_pop_lower_limit = int(request.form["point_pop_lower_limit"])
        # point_pop_upper_limit = int(request.form["point_pop_upper_limit"])
        village_pop_lower_limit = int(request.form["village_pop_lower_limit"])
        # village_pop_upper_limit = int(request.form["village_pop_upper_limit"])
        # village_size_lower_limit = int(request.form["village_size_lower_limit"])
        village_size_upper_limit = int(request.form["village_size_upper_limit"])
        # max_density_lower_limit = int(request.form["max_density_lower_limit"])
        # distance_threshold = float(request.form["distance_threshold"])
        # coast_distance_threshold = float(request.form["coast_distance_threshold"])
        # point_output_num = int(request.form["point_output_num"])

        setting = Setting(
            region,
            # population_param,
            # distance_param,
            point_pop_lower_limit,
            # point_pop_upper_limit,
            village_pop_lower_limit,
            # village_pop_upper_limit,
            # village_size_lower_limit,
            village_size_upper_limit,
            # max_density_lower_limit,
            # distance_threshold,
            # coast_distance_threshold,
            # point_output_num
        )

        result = calc_isolation.main(setting)

        elapsed_time = time.time() - start
        print(str(elapsed_time) + "[sec]")

        url = URL

        return render_template("index.html", result=result, setting=setting, url=url)
    else:
        return redirect(url_for('index'))


@app.route("/post_office")
def index_post_office():
    return render_template("faculty.html", faculty="post_office", faculty_ja="郵便局")


@app.route("/post_office/result", methods=["GET", "POST"])
def result_post_office():
    faculty = "post_office"
    region = request.form["region"]
    result = search_isolated_faculty.main(region, faculty)
    return render_template("faculty.html", faculty=faculty, faculty_ja="郵便局", result=result)


@app.route("/elementary_school")
def index_elementary_school():
    return render_template("faculty.html", faculty="elementary_school", faculty_ja="小学校")


@app.route("/elementary_school/result", methods=["GET", "POST"])
def result_elementary_school():
    faculty = "elementary_school"
    region = request.form["region"]
    result = search_isolated_faculty.main(region, faculty)
    return render_template("faculty.html", faculty=faculty, faculty_ja="小学校", result=result)


if __name__ == "__main__":
    app.run()
