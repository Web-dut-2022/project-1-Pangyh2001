from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import util
from django import forms

import random
import markdown2

class WikiForm(forms.Form):         #新内容类
    title = forms.CharField(label="Title", min_length=2, max_length=20)
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs=
        {"placeholder":"Use Markdown Syntax", "style":"height: 300px"}))

def index(request):#输入网址时进行的响应
    return render(request, "encyclopedia/index.html", {   #响应到模板index.html页面
        "entries": util.list_entries()           #entries是模板中的变量，把所有的markdown文件名字返回到entries列表
    })

def wiki(request, entry):   #显示条目的内容的模板，  参数entry由点击模板的有名分组时，反向解析到url中，传入参数
    entries = util.list_entries()   #把所有的markdown文件名字返回到entries列表
    if entry in entries:        #如果参数entry所引入的条目名称在列表中，则执行下一步，不在的话抛出error错误
        content = util.get_entry(entry)
        HTML_format = markdown2.markdown(content)   #将markdown转换为html，需要引入markdown2
        return render(request, "encyclopedia/wiki.html", {#返回到模板wiki.html
            "title":entry,
            "content":HTML_format
        })
    else:
        return HttpResponseRedirect("/error")

def error(request):      #错误方法，当有错误无法运行时，响应到encyclopedia目录下的error.html
    return render(request, "encyclopedia/error.html")


def search(request):            #用户点击提交按钮时，通过urls找到该方法
    if request.method=="GET":     #获取当前请求的方式，就是layout中的GET,意思是返回字符串
        query = request.GET.get("q")  #把搜索的内容赋给query
        if query == "" or query is None:  #输入的东西为空时，返回主界面
            return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))

    if util.get_entry(query) is not None:   #判断用户搜索的条目是否存在
        return redirect(wiki, query)        #存在的话就重定向到wiki方法，并传入条目名称

    entries = util.list_entries()           #下面处理不完整的情况
    result = []
    for e in entries:                       #遍历所有的条目名称赋给e，
        if query.lower() in e.lower() or e.lower() in query.lower():  #如果e与搜索的内容有关联,就把e加到结果列表中
            result.append(e)
    return render(request, "encyclopedia/search.html",{      #响应到模板search.html中，下面三个变量是返回的模板变量
        "query": query,
        "result": result,
        "is_found" : len(result) > 0
    })

def new(request):           #当用户通过页面点击新建时，通过反向解析到url找到该方法。
    if request.method=="POST":
        form = WikiForm(request.POST)
        if form.is_valid():         #如果表单没有错，则提取表单的标题和内容
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title) is None:   #如果标题是新的，就直接创建，并重定向到这个标题下面
                util.save_entry(title=title, content=content)
                return redirect(wiki, title)
            else:                                #如果标题不是空的，就返回new模板处理
                return render(request, "encyclopedia/new.html",{
                "form":form,
                "message": "Already Exist"
    })

    else:
        return render(request, "encyclopedia/new.html",{
        "form":WikiForm()
    })

def random_page(request):           #用户点击任意内容时，通过urls找到该方法
    entries=util.list_entries()     #从列表中随机选择一个条目名称，然后重定向到wiki方法实现随机页面
    random_entry = random.choice(entries)
    return redirect(wiki, random_entry)

def edit(request, entry):
    content = util.get_entry(entry)  #将编辑的这个条目内容赋给content
    if request.method=="POST":   #
        new_content = request.POST.get("content")
        util.save_entry(title=entry, content=new_content)
        return redirect(wiki, entry)

    if content:
        return render(request, "encyclopedia/edit.html",{
        "title": entry,
        "content" : util.get_entry(entry)
    })

    else:
        return HttpResponseRedirect(reverse('index'))
