# simple-website-engine
Very simple, no-frills static website maker with a very simple template engine. The templates are very dumb.

This wasn't well-thought out, it was more like a midnight project.

### Design
Creating the website is very simple. Design the page map using a page skeleton, and then define a set of simple HTML templates.

##### Skeleton
Design the layout of your website using yaml. The key for each page is a path; each page contains a template, an optional JSON file of data (to populate the template), and an optional set of subpages.

skeleton.json:
```json
{
  "": {
    "template": "templates/index.html"
  },
  "blog": {
    "template": "templates/blog-index.html",
    "subpages": {
      "first-blog-post": {
        "template": "templates/blog-post.html",
        "params": {
          "title": "My first blog post",
          "src": "/templates/blog/first-blog-post.html"
        }
      },
      "second-blog-post": {
        "template": "templates/blog-post.html",
        "params": {
          "title": "My second blog post",
          "src": "/templates/blog/second-blog-post.html"
        }
      }
    }
  },
  "faq": {
    "template": "templates/faq.html",
    "data": "data/faq.json"
  }
}
```

##### Templates
Templates are HTML files that will be compiled into static HTML files that will form your website. There are a few special operations that you can do with templates that you can't do otherwise:

1. Templates can import other templates. The imported template can either be a hardcoded path to another template, or a parameter passed into the template.
2. A template can take an HTML body by having `<template-body>` somewhere in the template. Then, if the template is ever included using `<template-include src="template-with-body.html">hello, world!</template-include>`, then `<template-body>` will be replaced with `hello, world!`.
3. JS executed in a template will have access to an object `_data`, which will be equal to the value of the `data` field specified for that page, if present.

For example, the `templates/blog/blog-post.html` template looks like this:
```html
<!- This is a comment. -->
<template-include src="../basic-template-layout.html" param-title="$title">
  <h1>$title</h1>
  <template-include src="$src"/>
</template-include>
```
and the `templates/basic-template-layout.html` template looks like this:
```html
<!doctype html>
<html>
<head>
  <title>$title</title>
</head>
<body>
  <!-- Simple header -->
  <h1>This is a header.</h1>
  <!-- Body -->
  <template-body>
  <!-- Simple footer -->
  <h1>This is a footer.</h1>
</body>
</html>
```

### Running the webserver
```sh
$ python compile.py
```

To view the webpage:
```sh
$ python -m http.server --directory out 8888
```
Then go to `localhost:8888` in your browser.

### Deployment
This is configured to build and deploy using GitHub pages.

Note that absolute paths are iffy when served as a project page (subdirectory of a domain) on GitHub pages (e.g., in the demo page). I don't know of a good way to fix this up, so beware.
