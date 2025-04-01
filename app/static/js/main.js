document.addEventListener('DOMContentLoaded', function() {
    const participantForm = document.getElementById('participantForm');
    const dateSelect = document.getElementById('date');
    
    // Fetch available dates
    fetch('/api/dates')
        .then(response => response.json())
        .then(dates => {
            // Populate date dropdown
            dates.forEach(date => {
                const option = document.createElement('option');
                option.value = date;
                option.textContent = date;
                dateSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching dates:', error);
            alert('日付の取得に失敗しました。');
        });
    
    // Form submission
    participantForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const participantData = {
            date: dateSelect.value,
            name: document.getElementById('name').value,
            contact: document.getElementById('contact').value
        };
        
        fetch('/api/participants', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(participantData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('参加者を登録しました！');
                participantForm.reset();
                dateSelect.value = ''; // 日付選択をリセット
            } else {
                alert('エラー: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error adding participant:', error);
            alert('参加者の登録に失敗しました。');
        });
    });
});