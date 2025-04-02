document.addEventListener('DOMContentLoaded', function() {
    // ローディング画面の要素を取得
    const loadingOverlay = document.getElementById('loadingOverlay');
    const submitButton = document.getElementById('submitButton');

    // ローディング画面の表示/非表示を制御する関数
    function toggleLoading(show) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
        submitButton.disabled = show;
    }

    // 日付データを取得してチェックボックスを生成
    fetch('/api/dates')
        .then(response => response.json())
        .then(dates => {
            const dateCheckboxes = document.getElementById('dateCheckboxes');
            dates.forEach(date => {
                const div = document.createElement('div');
                div.className = 'date-option';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `date-${date}`;
                checkbox.value = date;
                checkbox.name = 'dates';
                
                const label = document.createElement('label');
                label.htmlFor = `date-${date}`;
                label.textContent = date;
                
                div.appendChild(checkbox);
                div.appendChild(label);
                dateCheckboxes.appendChild(div);
            });
        })
        .catch(error => console.error('Error:', error));

    // フォーム送信処理
    document.getElementById('participantForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // 選択された日付を取得
        const selectedDates = Array.from(document.querySelectorAll('input[name="dates"]:checked'))
            .map(checkbox => checkbox.value);
            
        // バリデーション
        const dateError = document.getElementById('dateError');
        if (selectedDates.length === 0) {
            dateError.style.display = 'block';
            return;
        }
        dateError.style.display = 'none';

        const name = document.getElementById('name').value;
        const contact = document.getElementById('contact').value;

        // ローディング画面を表示
        toggleLoading(true);

        // 各選択日付に対して登録処理を実行
        try {
            const promises = selectedDates.map(date => 
                fetch('/api/participants', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        date: date,
                        name: name,
                        contact: contact
                    })
                })
            );

            await Promise.all(promises);
            alert('登録が完了しました');
            document.getElementById('participantForm').reset();
        } catch (error) {
            console.error('Error:', error);
            alert('登録中にエラーが発生しました');
        } finally {
            // ローディング画面を非表示
            toggleLoading(false);
        }
    });
});