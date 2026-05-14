let currentTrackInfo = null;
let currentSpotifyCodeSvg = null;
let currentDownloadUrl = null;

const API_BASE_URL = ''; 

const spotifyUrlInput = document.getElementById('spotifyUrl');
const urlValidation = document.getElementById('urlValidation');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const generateBtn = document.getElementById('generateBtn');
const generateIcon = document.getElementById('generateIcon');
const generateText = document.getElementById('generateText');
const previewSection = document.getElementById('previewSection');
const trackInfoTitle = document.getElementById('trackInfoTitle');
const trackInfoContent = document.getElementById('trackInfoContent');
const spotifyCodeSection = document.getElementById('spotifyCodeSection');
const spotifyCodeDisplay = document.getElementById('spotifyCodeDisplay');
const downloadStlBtn = document.getElementById('downloadStlBtn');

document.addEventListener('DOMContentLoaded', function() {
    spotifyUrlInput.addEventListener('input', handleUrlChange);
    spotifyUrlInput.addEventListener('paste', function(e) {
        setTimeout(() => handleUrlChange(e), 10);
    });
});

function validateSpotifyUrl(url) {
    const spotifyRegex = /^https:\/\/open\.spotify\.com\/(track|album|playlist|artist)\/[a-zA-Z0-9]+(\?.*)?$/;
    return spotifyRegex.test(url);
}

function extractSpotifyId(url) {
    const match = url.match(/\/([a-zA-Z0-9]+)(\?|$)/);
    return match ? match[1] : null;
}

function getSpotifyType(url) {
    const match = url.match(/\/(track|album|playlist|artist)\//);
    return match ? match[1] : null;
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function updateValidationIcon(isValid) {
    if (spotifyUrlInput.value === '') {
        urlValidation.classList.add('hidden');
        return;
    }

    urlValidation.classList.remove('hidden');
    
    if (isValid) {
        urlValidation.innerHTML = `
            <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
        `;
    } else {
        urlValidation.innerHTML = `
            <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
        `;
    }
}

function setProcessingState(isProcessing) {
    generateBtn.disabled = isProcessing;
    
    if (isProcessing) {
        generateIcon.innerHTML = `
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        `;
        generateText.textContent = 'Processing...';
    } else {
        generateIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        `;
        generateText.textContent = 'Generate';
    }
}

function handleUrlChange(e) {
    const url = e.target.value;
    const isValid = validateSpotifyUrl(url);
    
    updateValidationIcon(isValid);
    generateBtn.disabled = !isValid;
    hideError();
    previewSection.classList.add('hidden');
    
    setProcessingState(false);
}

function scrollToCreate() {
    document.getElementById('create').scrollIntoView({ behavior: 'smooth' });
}

async function fetchSpotifyCodeSvg(spotifyUrl) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/generate_spotify_code/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "spotify_url": spotifyUrl })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.preview_url) {
            spotifyCodeDisplay.innerHTML = `<img src="${data.preview_url}" alt="Spotify Code" class="w-full">`;
            spotifyCodeSection.classList.remove('hidden');
        }

        return data;
    } catch (error) {
        console.error("Failed to fetch Spotify Code:", error);
        throw error;
    }
}

async function fetchTrackInfo(spotifyUrl) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/spotify/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ spotify_url: spotifyUrl })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.warn('Backend not available, using mock track info:', error.message);
        
        const spotifyType = getSpotifyType(spotifyUrl);
        const mockTrackInfo = {
            track: {
                title: "Blinding Lights",
                artist: "The Weeknd",
                album: "After Hours",
                image: "https://images.pexels.com/photos/167092/pexels-photo-167092.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&dpr=2",
                duration: "3:20",
                release_date: "2019"
            },
            album: {
                title: "After Hours",
                artist: "The Weeknd",
                image: "https://images.pexels.com/photos/167092/pexels-photo-167092.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&dpr=2",
                tracks: 14,
                release_date: "2020"
            },
            playlist: {
                title: "Today's Top Hits",
                creator: "Spotify",
                image: "https://images.pexels.com/photos/167092/pexels-photo-167092.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&dpr=2",
                tracks: 50,
                followers: "32M"
            },
            artist: {
                title: "The Weeknd",
                image: "https://images.pexels.com/photos/167092/pexels-photo-167092.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&dpr=2",
                followers: "85M",
                monthly_listeners: "107M"
            }
        };

        return {
            type: spotifyType,
            data: mockTrackInfo[spotifyType],
            id: extractSpotifyId(spotifyUrl)
        };
    }
}

async function generateKeychain() {
    const spotifyUrl = spotifyUrlInput.value;
    
    if (!validateSpotifyUrl(spotifyUrl)) {
        showError('Please enter a valid Spotify URL');
        return;
    }

    setProcessingState(true);
    hideError();

    try {
        const [svgData, trackData] = await Promise.all([
            fetchSpotifyCodeSvg(spotifyUrl),
            fetchTrackInfo(spotifyUrl)
        ]);

        currentSpotifyCodeSvg = svgData;
        currentTrackInfo = trackData;
        currentDownloadUrl = svgData.download_url || null;

        displayPreview(trackData, svgData);
    } catch (error) {
        showError(error.message || 'Failed to process Spotify URL');
    } finally {
        setProcessingState(false);
    }
}

function displayPreview(trackInfo, svgData) {
    trackInfoTitle.textContent = `${trackInfo.type.charAt(0).toUpperCase() + trackInfo.type.slice(1)} Information`;
    
    trackInfoContent.innerHTML = renderTrackInfo(trackInfo);
    
    if (svgData && svgData.preview_url) {
        spotifyCodeDisplay.innerHTML = `<img src="${svgData.preview_url}" alt="Spotify Code" class="w-full">`;
        spotifyCodeSection.classList.remove('hidden');
    }

    if (svgData && svgData.download_url) {
        downloadStlBtn.href = svgData.download_url;
        downloadStlBtn.setAttribute('download', svgData.download_url.split('/').pop() || 'soundchain-keychain.stl');
        downloadStlBtn.setAttribute('aria-disabled', 'false');
        downloadStlBtn.classList.remove('opacity-50', 'pointer-events-none');
    } else {
        downloadStlBtn.href = '#';
        downloadStlBtn.setAttribute('aria-disabled', 'true');
        downloadStlBtn.classList.add('opacity-50', 'pointer-events-none');
    }
    
    previewSection.classList.remove('hidden');
}

function renderTrackInfo(trackInfo) {
    const { type, data } = trackInfo;

    switch (type) {
        case 'track':
            return `
                <div class="flex items-center space-x-4">
                    <img src="${data.image}" alt="Album artwork" class="w-16 h-16 rounded-lg object-cover">
                    <div>
                        <h5 class="font-semibold">${data.title}</h5>
                        <p class="text-gray-600">${data.artist}</p>
                        <p class="text-sm text-gray-500">${data.album} • ${data.duration}</p>
                    </div>
                </div>
            `;
        case 'album':
            return `
                <div class="flex items-center space-x-4">
                    <img src="${data.image}" alt="Album artwork" class="w-16 h-16 rounded-lg object-cover">
                    <div>
                        <h5 class="font-semibold">${data.title}</h5>
                        <p class="text-gray-600">${data.artist}</p>
                        <p class="text-sm text-gray-500">${data.tracks} tracks • ${data.release_date}</p>
                    </div>
                </div>
            `;
        case 'playlist':
            return `
                <div class="flex items-center space-x-4">
                    <img src="${data.image}" alt="Playlist artwork" class="w-16 h-16 rounded-lg object-cover">
                    <div>
                        <h5 class="font-semibold">${data.title}</h5>
                        <p class="text-gray-600">by ${data.creator}</p>
                        <p class="text-sm text-gray-500">${data.tracks} tracks • ${data.followers} followers</p>
                    </div>
                </div>
            `;
        case 'artist':
            return `
                <div class="flex items-center space-x-4">
                    <img src="${data.image}" alt="Artist photo" class="w-16 h-16 rounded-lg object-cover">
                    <div>
                        <h5 class="font-semibold">${data.title}</h5>
                        <p class="text-gray-600">Artist</p>
                        <p class="text-sm text-gray-500">${data.followers} followers • ${data.monthly_listeners} monthly listeners</p>
                    </div>
                </div>
            `;
        default:
            return '<p class="text-gray-500">Unable to load track information</p>';
    }
}

