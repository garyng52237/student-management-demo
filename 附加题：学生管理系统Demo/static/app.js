const $ = (selector) => document.querySelector(selector);

function showMessage(message, isError = false) {
  const element = $("#message");
  element.textContent = message || "";
  element.className = isError ? "message error" : "message";
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) {
    throw new Error(result.message || "请求失败");
  }
  return result.data;
}

function fillClassSelect(select, classes, firstOption) {
  select.innerHTML = firstOption;
  classes.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.class_id;
    option.textContent = item.class_name;
    select.appendChild(option);
  });
}

async function loadClasses() {
  const classes = await request("/api/classes");
  const studentClass = $("#student-class");
  const filterClass = $("#filter-class");
  fillClassSelect(studentClass, classes, '<option value="">未分配</option>');
  fillClassSelect(filterClass, classes, '<option value="">全部班级</option>');

  const table = $("#class-table");
  table.innerHTML = "";
  classes.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.class_id}</td><td></td><td></td>`;
    row.children[1].textContent = item.class_name;
    const edit = document.createElement("button");
    edit.textContent = "编辑";
    edit.onclick = () => {
      $("#class-id").value = item.class_id;
      $("#class-name").value = item.class_name;
    };
    const remove = document.createElement("button");
    remove.textContent = "删除";
    remove.onclick = () => deleteClass(item.class_id);
    row.children[2].append(edit, remove);
    table.appendChild(row);
  });
}

async function loadStudents(classId = "") {
  const query = classId ? `?class_id=${encodeURIComponent(classId)}` : "";
  const students = await request(`/api/students${query}`);
  const table = $("#student-table");
  table.innerHTML = "";
  students.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.student_id}</td><td></td><td></td><td></td><td></td><td></td>`;
    row.children[1].textContent = item.student_name;
    row.children[2].textContent = item.gender || "";
    row.children[3].textContent = item.age ?? "";
    row.children[4].textContent = item.class_name || "未分配";
    const edit = document.createElement("button");
    edit.textContent = "编辑";
    edit.onclick = () => {
      $("#student-id").value = item.student_id;
      $("#student-name").value = item.student_name;
      $("#gender").value = item.gender || "";
      $("#age").value = item.age ?? "";
      $("#student-class").value = item.class_id || "";
    };
    const remove = document.createElement("button");
    remove.textContent = "删除";
    remove.onclick = () => deleteStudent(item.student_id);
    row.children[5].append(edit, remove);
    table.appendChild(row);
  });
}

async function deleteClass(id) {
  if (!confirm("确定删除这个班级吗？")) return;
  try {
    await request(`/api/classes/${id}`, { method: "DELETE" });
    showMessage("班级删除成功");
    resetClassForm();
    await loadClasses();
    await loadStudents($("#filter-class").value);
  } catch (error) { showMessage(error.message, true); }
}

async function deleteStudent(id) {
  if (!confirm("确定删除这个学生吗？")) return;
  try {
    await request(`/api/students/${id}`, { method: "DELETE" });
    showMessage("学生删除成功");
    resetStudentForm();
    await loadStudents($("#filter-class").value);
  } catch (error) { showMessage(error.message, true); }
}

function resetClassForm() {
  $("#class-form").reset();
  $("#class-id").value = "";
}

function resetStudentForm() {
  $("#student-form").reset();
  $("#student-id").value = "";
}

$("#class-form").onsubmit = async (event) => {
  event.preventDefault();
  const id = $("#class-id").value;
  const url = id ? `/api/classes/${id}` : "/api/classes";
  const method = id ? "PUT" : "POST";
  try {
    await request(url, { method, body: JSON.stringify({ class_name: $("#class-name").value }) });
    showMessage(id ? "班级修改成功" : "班级新增成功");
    resetClassForm();
    await loadClasses();
  } catch (error) { showMessage(error.message, true); }
};

$("#student-form").onsubmit = async (event) => {
  event.preventDefault();
  const id = $("#student-id").value;
  const body = {
    student_name: $("#student-name").value,
    gender: $("#gender").value,
    age: $("#age").value,
    class_id: $("#student-class").value,
  };
  try {
    await request(id ? `/api/students/${id}` : "/api/students", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(body),
    });
    showMessage(id ? "学生修改成功" : "学生新增成功");
    resetStudentForm();
    await loadStudents($("#filter-class").value);
  } catch (error) { showMessage(error.message, true); }
};

$("#class-cancel").onclick = resetClassForm;
$("#student-cancel").onclick = resetStudentForm;
$("#filter-class").onchange = (event) => loadStudents(event.target.value).catch((error) => showMessage(error.message, true));

Promise.all([loadClasses(), loadStudents()]).catch((error) => showMessage(error.message, true));
