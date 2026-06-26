# Note

个人笔记文档，基于 Sphinx 构建，通过 Read the Docs 自动部署。

## 在线文档

https://note.readthedocs.io

## 本地构建

```bash
pip install -r requirements.txt
cd docs && make html
```

打开 `docs/_build/html/index.html` 查看。

## 自动部署

每次推送到 `main` 分支，Read the Docs 会自动触发构建并更新文档。
