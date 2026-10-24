# student-management-demo
# 学生管理系统 Demo

一个使用 JavaScript + Python Flask + SQLite 实现的最小学生管理系统，满足笔试附加题的基本要求。

## 功能

- 班级新增、查询、修改、删除；
- 学生新增、查询、修改、删除；
- 学生与班级关系保存；
- 选择班级后筛选学生；
- 使用按钮、输入框、下拉框和表格。

## 运行方法

```bash
cd 学生管理系统
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py
```

浏览器打开 <http://127.0.0.1:5000>。

首次运行会自动创建 `student.db` 和三张数据表。

## 备注

本项目的整体架构设计、功能实现与测试由本人完成，开发过程中使用本地部署的 35B 模型辅助代码编写与优化。
