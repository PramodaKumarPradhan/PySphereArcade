document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const fileInput = document.getElementById('fileInput');
    const addFilesBtn = document.getElementById('addFilesBtn');
    const mediaGrid = document.getElementById('mediaGrid');
    const mainPlayer = document.getElementById('mainPlayer');
    const audioVisualizer = document.getElementById('audioVisualizer');
    const nowPlayingTitle = document.getElementById('nowPlayingTitle');
    
    // Albums elements
    const createAlbumBtn = document.getElementById('createAlbumBtn');
    const createAlbumModal = document.getElementById('createAlbumModal');
    const cancelAlbumBtn = document.getElementById('cancelAlbumBtn');
    const saveAlbumBtn = document.getElementById('saveAlbumBtn');
    const albumNameInput = document.getElementById('albumNameInput');
    const albumList = document.getElementById('albumList');
    const currentAlbumTitle = document.getElementById('currentAlbumTitle');

    // State
    let allMedia = [];
    let albums = {}; // { 'albumId': { name: 'Album Name', media: ['mediaId1', 'mediaId2'] } }
    let currentAlbum = 'all';

    // Canvas Visualizer
    const canvas = document.getElementById('visualizerCanvas');
    const ctx = canvas.getContext('2d');
    let audioCtx, analyser, source, dataArray, bufferLength;
    let visualizerInitialized = false;

    function resizeCanvas() {
        if(canvas) {
            canvas.width = canvas.parentElement.offsetWidth;
            canvas.height = canvas.parentElement.offsetHeight / 3;
        }
    }
    window.addEventListener('resize', resizeCanvas);
    setTimeout(resizeCanvas, 100);

    function setupAudioContext() {
        if(!visualizerInitialized) {
            try {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                source = audioCtx.createMediaElementSource(mainPlayer);
                source.connect(analyser);
                analyser.connect(audioCtx.destination);
                analyser.fftSize = 128; // Lower for chunkier bars
                bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
                visualizerInitialized = true;
                drawVisualizer();
            } catch(e) {
                console.error("Audio Context setup failed", e);
            }
        }
    }

    function drawVisualizer() {
        if(!visualizerInitialized) return;
        requestAnimationFrame(drawVisualizer);

        analyser.getByteFrequencyData(dataArray);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / bufferLength) * 2;
        let barHeight;
        let x = 0;

        for(let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i] / 1.5;
            ctx.fillStyle = `rgba(107, 76, 230, ${Math.max(0.2, barHeight/150)})`;
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }
    }

    // Handlers
    addFilesBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        if(files.length === 0) return;

        files.forEach(file => {
            const id = 'media_' + Date.now() + Math.random().toString(36).substr(2, 9);
            const mediaItem = {
                id,
                file,
                name: file.name,
                type: file.type.startsWith('video/') ? 'video' : 'audio',
                url: URL.createObjectURL(file)
            };
            allMedia.push(mediaItem);
        });

        renderMediaGrid();
        
        // Clear input to allow re-selecting same files
        fileInput.value = '';
    });

    function renderMediaGrid() {
        mediaGrid.innerHTML = '';
        
        let mediaToRender = allMedia;
        if(currentAlbum !== 'all') {
            const albumMediaIds = albums[currentAlbum] ? albums[currentAlbum].media : [];
            mediaToRender = allMedia.filter(m => albumMediaIds.includes(m.id));
        }

        if(mediaToRender.length === 0) {
            mediaGrid.innerHTML = `
                <div class="empty-state">
                    <span class="material-icons-round">folder_open</span>
                    <p>No media files here.</p>
                </div>
            `;
            return;
        }

        mediaToRender.forEach(media => {
            const el = document.createElement('div');
            el.className = 'media-item';
            
            let optionsHTML = `<option value="">Add to...</option>`;
            Object.keys(albums).forEach(albumId => {
                optionsHTML += `<option value="${albumId}">${albums[albumId].name}</option>`;
            });

            el.innerHTML = `
                <div class="media-icon-wrapper" onclick="playMedia('${media.id}')">
                    ${media.type === 'video' 
                        ? '<span class="material-icons-round">movie</span>' 
                        : '<span class="material-icons-round">music_note</span>'}
                    <div class="play-overlay material-icons-round" style="position: absolute; color: white; opacity: 0; transition: 0.2s;">play_arrow</div>
                </div>
                <div class="media-info">
                    <div class="media-title" title="${media.name}">${media.name}</div>
                    <div class="media-actions">
                        <span class="media-type">${media.type}</span>
                        <select class="add-to-album-select" onchange="addToAlbum('${media.id}', this.value); this.value=''">
                            ${optionsHTML}
                        </select>
                    </div>
                </div>
            `;
            mediaGrid.appendChild(el);
        });
    }

    window.playMedia = (id) => {
        const media = allMedia.find(m => m.id === id);
        if(!media) return;

        mainPlayer.src = media.url;
        
        // Try playing
        mainPlayer.play().then(() => {
            if(media.type === 'audio') {
                setupAudioContext();
                if(audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
            }
        }).catch(err => console.log("Playback interrupted or requires interaction", err));

        if(media.type === 'video') {
            mainPlayer.style.display = 'block';
            mainPlayer.style.height = '100%';
            mainPlayer.style.position = 'static';
            audioVisualizer.style.display = 'none';
        } else {
            // Audio layout
            mainPlayer.style.display = 'block';
            mainPlayer.style.height = '50px';
            mainPlayer.style.position = 'absolute';
            mainPlayer.style.bottom = '10px';
            mainPlayer.style.zIndex = '10';
            mainPlayer.style.width = '50%';
            
            audioVisualizer.style.display = 'flex';
            nowPlayingTitle.textContent = media.name;
        }
    };

    window.addToAlbum = (mediaId, albumId) => {
        if(!albumId) return;
        if(!albums[albumId]) return;
        
        if(!albums[albumId].media.includes(mediaId)){
            albums[albumId].media.push(mediaId);
        }
        
        // Alert briefly
        const albumName = albums[albumId].name;
        alert(`Added to ${albumName}`);
    };

    // Albums
    createAlbumBtn.addEventListener('click', () => {
        createAlbumModal.classList.add('active');
        albumNameInput.focus();
    });

    const closeModal = () => {
        createAlbumModal.classList.remove('active');
        albumNameInput.value = '';
    };

    cancelAlbumBtn.addEventListener('click', closeModal);

    saveAlbumBtn.addEventListener('click', () => {
        const name = albumNameInput.value.trim();
        if(name) {
            const id = 'album_' + Date.now();
            albums[id] = { name, media: [] };
            renderAlbums();
            renderMediaGrid(); // update dropdowns
            closeModal();
        }
    });

    function renderAlbums() {
        const allItem = albumList.querySelector('li[data-id="all"]');
        albumList.innerHTML = '';
        albumList.appendChild(allItem);

        Object.keys(albums).forEach(id => {
            const li = document.createElement('li');
            li.dataset.id = id;
            li.innerHTML = `${albums[id].name}`;
            albumList.appendChild(li);
        });

        albumList.querySelectorAll('li').forEach(li => {
            li.addEventListener('click', () => {
                albumList.querySelectorAll('li').forEach(l => l.classList.remove('active'));
                li.classList.add('active');
                currentAlbum = li.dataset.id;
                currentAlbumTitle.textContent = currentAlbum === 'all' ? 'All Media' : albums[currentAlbum].name;
                renderMediaGrid();
            });
        });
        
        // Re-apply active class correctly if re-rendered
        albumList.querySelectorAll('li').forEach(li => {
            if(li.dataset.id === currentAlbum) {
                li.classList.add('active');
            }
        });
    }

    renderAlbums();
});
