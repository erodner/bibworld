import os
from os.path import expanduser
from os.path import join as pjoin

import fastapi
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from starlette.responses import FileResponse

from bibdb import bibdb

homepath = expanduser("~")

mybib = None

htmlroot = "example-template-jinja2"
bibfile = pjoin(homepath, "publications", "paper.bib")
pdfdir = pjoin(homepath, "publications-pdfs")
defaulttemplate = "erikslist.html"

# fixed settings
# bibtex keys that will be exported and provided in the downloaded bibtex keys
exported_bibkeys = {
    "title",
    "author",
    "booktitle",
    "pages",
    "journal",
    "year",
    "volume",
    "number",
    "doi",
}


def loaddb(oldstamp=None):
    """ server initialization (loading bibtex keys and setting up the cache) """
    mybib = bibdb()
    mybib.readFromBibTex(bibfile)
    mybib.addAuxFiles(os.path.join(pdfdir, "%s.pdf"), "pdf")
    # compatibility for the old format
    mybib.addAuxFiles(os.path.join(pdfdir, "%s.pdf.teaser.png"), "teaser")
    mybib.addAuxFiles(
        os.path.join(pdfdir, "%s.teaser.png"), "teaser", removeIfUnavailable=False
    )
    mybib.addAuxFiles(os.path.join(pdfdir, "%s.presentation.pdf"), "presentation")
    mybib.addAuxFiles(os.path.join(pdfdir, "%s.supplementary.pdf"), "supplementary")

    return mybib


mybib = loaddb()

# FastAPI initialization

app = FastAPI()

app.mount("/static", StaticFiles(directory=htmlroot), name="static")
templates = Jinja2Templates(directory=htmlroot)

#
# Helper functions
#
# def webserver_send_file(fn, mimetype):
#    # http://stackoverflow.com/questions/5410255/preferred-method-for-downloading-a-file-generated-on-the-fly-in-flask
#    basefn = fn.replace(pdfdir, "/staticfiles/")
#    response = make_response()
#    response.headers["Cache-Control"] = "no-cache"
#    response.headers["Content-Type"] = mimetype
#    response.headers["X-Accel-Redirect"] = basefn
#    print("Sending file {} as {} with X-Accel-Direct".format(fn, basefn))
#    return response


#
# API Definition
#
@app.get("/", response_class=HTMLResponse)
def start(request: Request, template: Optional[str] = defaulttemplate):
    return templates.TemplateResponse(
        template, {"request": request, "refs": mybib.getReferences()}
    )


@app.get("/author/{author}", response_class=HTMLResponse)
def print_author(
    author: str, request: Request, template: Optional[str] = defaulttemplate
):
    refs = mybib.getReferences(author=author)
    return templates.TemplateResponse(template, {"request": request, "refs": refs})


@app.get("/searchbyfield/{field}/{term}", response_class=HTMLResponse)
def print_searchfield(
    field: str, term: str, request: Request, template: Optional[str] = defaulttemplate
):
    refs = mybib.getReferences(field=term)
    return templates.TemplateResponse(template, {"request": request, "refs": refs})


@app.get("/search/{term}", response_class=HTMLResponse)
def print_search(
    term: str, request: Request, template: Optional[str] = defaulttemplate
):
    refs = mybib.searchReferences(term)
    return templates.TemplateResponse(template, {"request": request, "refs": refs})


@app.get("/year/{year}", response_class=HTMLResponse)
def print_year(year: str, request: Request, template: Optional[str] = defaulttemplate):
    refs = mybib.getReferences(year=year)
    return templates.TemplateResponse(template, {"request": request, "refs": refs})


@app.get("/bib/{bibid}", response_class=HTMLResponse)
def print_bibtex(bibid: str, request: Request):
    return mybib.getBibtexEntry(
        bibid, newlinestr="<br>", exported_keys=exported_bibkeys
    )


@app.get("/bibsearch/{term}", response_class=HTMLResponse)
def print_bibtexsearch(term: str, request: Request):
    refs = mybib.searchReferences(term)
    output = ""
    for bibid in refs:
        output = (
            output
            + mybib.getBibtexEntry(
                bibid, newlinestr="<br>", exported_keys=exported_bibkeys
            )
            + "<br>"
        )
    return output


def send_aux_file(bibid, tag, mimetype):
    ref = mybib.getReference(bibid)
    if tag in ref:
        file_location = ref[tag]
        return FileResponse(file_location, media_type=mimetype)

    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/pdf/{bibid}.pdf")
def print_pdf(bibid: str):
    return send_aux_file(bibid, "pdf", "application/pdf")


@app.get("/teaser/{bibid}")
def print_teaser(bibid: str):
    return send_aux_file(bibid, "teaser", "image/png")


@app.get("/presentation/{bibid}.pdf")
def print_presentation(bibid: str):
    return send_aux_file(bibid, "presentation", "application/pdf")


@app.get("/supplementary/{bibid}.pdf")
def print_supplementary(bibid: str):
    return send_aux_file(bibid, "supplementary", "application/pdf")


@app.get("/refresh")
def refresh():
    # try to perform a git update before the refresh
    gitdir = os.path.dirname(bibfile)

    try:
        import git

        g = git.cmd.Git(gitdir)
        gitmsg = g.pull("origin", "master")
        print("Git update successfull: {}".format(gitmsg))
    except git.GitCommandError as e:
        print("Git error: {} for {}".format(e, gitdir))

    # reread everything
    loaddb()

    response = RedirectResponse(url="/")
    return response


#############################################################

# from bibgraph import getGraphJSON
# app.jinja_env.globals.update(getgraph=getGraphJSON)

# if __name__ == "__main__":
#    app.run(host="0.0.0.0", debug=True)
