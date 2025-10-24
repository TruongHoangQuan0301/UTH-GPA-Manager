// Utility functions
function calculateGPA(grades) {
    if (grades.length === 0) return 0;
    
    let totalPoints = 0;
    let totalCredits = 0;
    
    grades.forEach(grade => {
        totalPoints += grade.grade4 * grade.credits;
        totalCredits += grade.credits;
    });
    
    return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : 0;
}

function convertTo4Scale(grade10) {
    if (grade10 >= 8.5) return 4.0;
    if (grade10 >= 8.0) return 3.5;
    if (grade10 >= 7.0) return 3.0;
    if (grade10 >= 6.0) return 2.5;
    if (grade10 >= 5.5) return 2.0;
    if (grade10 >= 5.0) return 1.5;
    if (grade10 >= 4.0) return 1.0;
    if (grade10 >= 2.1) return 0.5;
    return 0.0;
}

// Load subjects from JSON
async function loadSubjects() {
    try {
        const response = await fetch('/api/subjects');
        const subjects = await response.json();
        
        // Populate all subject select elements
        document.querySelectorAll('.subject-select').forEach(select => {
            subjects.forEach(subject => {
                const option = new Option(subject.name, subject.id);
                select.add(option);
            });
        });
    } catch (error) {
        console.error('Error loading subjects:', error);
        showToast('Lỗi tải danh sách môn học', 'error');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type === 'error' ? 'danger' : 'success'} text-white`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-body">
            ${message}
            <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Handle form submissions
document.querySelectorAll('.semester-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const semester = form.dataset.semester;
        const subject = form.querySelector(`#subject-${semester}`).value;
        const credits = parseFloat(form.querySelector(`#credits-${semester}`).value);
        const grade10 = parseFloat(form.querySelector(`#grade-${semester}`).value);
        
        if (!subject || isNaN(credits) || isNaN(grade10)) {
            showToast('Vui lòng điền đầy đủ thông tin', 'error');
            return;
        }
        
        try {
            const grade4 = convertTo4Scale(grade10);
            const response = await fetch('/api/grades', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    semester,
                    subject,
                    credits,
                    grade10,
                    grade4
                })
            });
            
            if (response.ok) {
                // Add grade to table
                const tbody = document.querySelector(`#grades-${semester}`);
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${subject}</td>
                    <td>${credits}</td>
                    <td>${grade10.toFixed(1)}</td>
                    <td>${grade4.toFixed(1)}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteGrade(this)">
                            🗑️ Xóa
                        </button>
                    </td>
                `;
                
                // Update semester GPA
                updateSemesterGPA(semester);
                
                // Reset form
                form.reset();
                showToast('Đã thêm điểm thành công');
            } else {
                throw new Error('Failed to save grade');
            }
        } catch (error) {
            console.error('Error saving grade:', error);
            showToast('Lỗi khi lưu điểm', 'error');
        }
    });
});

// Delete grade
function deleteGrade(button) {
    if (confirm('Bạn có chắc chắn muốn xóa điểm này?')) {
        const row = button.closest('tr');
        const tbody = row.parentElement;
        const semester = tbody.id.split('-')[1];
        
        row.remove();
        updateSemesterGPA(semester);
        showToast('Đã xóa điểm');
    }
}

// Update semester GPA
function updateSemesterGPA(semester) {
    const grades = [];
    const tbody = document.querySelector(`#grades-${semester}`);
    
    tbody.querySelectorAll('tr').forEach(row => {
        const cells = row.cells;
        grades.push({
            credits: parseFloat(cells[1].textContent),
            grade4: parseFloat(cells[3].textContent)
        });
    });
    
    const gpa = calculateGPA(grades);
    document.querySelector(`#gpa-${semester}`).textContent = gpa;
}

// Calculate total GPA
document.getElementById('calculateTotalGPA').addEventListener('click', () => {
    const allGrades = [];
    
    document.querySelectorAll('[id^="grades-"]').forEach(tbody => {
        tbody.querySelectorAll('tr').forEach(row => {
            const cells = row.cells;
            allGrades.push({
                credits: parseFloat(cells[1].textContent),
                grade4: parseFloat(cells[3].textContent)
            });
        });
    });
    
    if (allGrades.length === 0) {
        showToast('Chưa có dữ liệu điểm nào', 'error');
        return;
    }
    
    const totalGPA = calculateGPA(allGrades);
    const totalCredits = allGrades.reduce((sum, grade) => sum + grade.credits, 0);
    
    document.getElementById('totalGPA').textContent = totalGPA;
    document.getElementById('totalCredits').textContent = totalCredits;
    document.getElementById('totalGPAResult').style.display = 'block';
});

// Export to Excel
document.getElementById('exportExcel').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/export-excel');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'GPA_Report.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            showToast('Đã xuất file Excel thành công');
        } else {
            throw new Error('Failed to export Excel');
        }
    } catch (error) {
        console.error('Error exporting Excel:', error);
        showToast('Lỗi khi xuất file Excel', 'error');
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSubjects();
});