// Dummy file
// Global variables
let currentTrackInfo = null;
let currentSpotifyCodeSvg = null;

// Configuration - Update these URLs to match your FastAPI backend
//const API_BASE_URL = 'http://localhost:8000'; // Change this to your FastAPI server URL
const API_BASE_URL = ''; // Change this to your FastAPI server URL

// DOM Elements
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

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    spotifyUrlInput.addEventListener('input', handleUrlChange);
    spotifyUrlInput.addEventListener('paste', function(e) {
        // Handle paste event with a small delay to get the pasted content
        setTimeout(() => handleUrlChange(e), 10);
    });
});

// Utility functions
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

// Event handlers
function handleUrlChange(e) {
    const url = e.target.value;
    const isValid = validateSpotifyUrl(url);
    
    updateValidationIcon(isValid);
    generateBtn.disabled = !isValid;
    hideError();
    previewSection.classList.add('hidden');
    
    // Reset button state
    setProcessingState(false);
}

function scrollToCreate() {
    document.getElementById('create').scrollIntoView({ behavior: 'smooth' });
}

// API functions - These will communicate with your FastAPI backend
async function fetchSpotifyCodeSvg(spotifyUrl) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/generate_spotify_code`, {
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
        return data.svg_content;
    } catch (error) {
        console.warn('Backend not available, using mock Spotify Code SVG:', error.message);
        
        // Fallback to mock SVG for development/testing
        return `<svg width="320" height="80" viewBox="0 0 320 80" xmlns="http://www.w3.org/2000/svg">
            <rect width="320" height="80" fill="#FFFFFF"/>
            <g fill="#000000">
                <rect x="20" y="20" width="4" height="40"/>
                <rect x="28" y="15" width="2" height="50"/>
                <rect x="34" y="25" width="6" height="30"/>
                <rect x="44" y="10" width="3" height="60"/>
                <rect x="52" y="20" width="4" height="40"/>
                <rect x="60" y="18" width="2" height="44"/>
                <rect x="66" y="22" width="5" height="36"/>
                <rect x="75" y="12" width="3" height="56"/>
                <rect x="82" y="25" width="4" height="30"/>
                <rect x="90" y="15" width="2" height="50"/>
                <rect x="96" y="20" width="6" height="40"/>
                <rect x="106" y="18" width="3" height="44"/>
                <rect x="114" y="22" width="4" height="36"/>
                <rect x="122" y="10" width="2" height="60"/>
                <rect x="128" y="25" width="5" height="30"/>
                <rect x="137" y="15" width="3" height="50"/>
                <rect x="144" y="20" width="4" height="40"/>
                <rect x="152" y="12" width="2" height="56"/>
                <rect x="158" y="25" width="6" height="30"/>
                <rect x="168" y="18" width="3" height="44"/>
                <rect x="175" y="20" width="4" height="40"/>
                <rect x="183" y="15" width="2" height="50"/>
                <rect x="189" y="22" width="5" height="36"/>
                <rect x="198" y="10" width="3" height="60"/>
                <rect x="205" y="25" width="4" height="30"/>
                <rect x="213" y="18" width="2" height="44"/>
                <rect x="219" y="20" width="6" height="40"/>
                <rect x="229" y="15" width="3" height="50"/>
                <rect x="236" y="22" width="4" height="36"/>
                <rect x="244" y="12" width="2" height="56"/>
                <rect x="250" y="25" width="5" height="30"/>
                <rect x="259" y="18" width="3" height="44"/>
                <rect x="266" y="20" width="4" height="40"/>
                <rect x="274" y="15" width="2" height="50"/>
                <rect x="280" y="10" width="6" height="60"/>
            </g>
        </svg>`;
    }
}

async function fetchTrackInfo(spotifyUrl) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/get-track-info`, {
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
        
        // Fallback to mock data for development/testing
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

// Main generation function
async function generateKeychain() {
    const spotifyUrl = spotifyUrlInput.value;
    
    if (!validateSpotifyUrl(spotifyUrl)) {
        showError('Please enter a valid Spotify URL');
        return;
    }

    setProcessingState(true);
    hideError();

    try {
        // Fetch both the Spotify Code SVG and track information
        const [svgData, trackData] = await Promise.all([
            fetchSpotifyCodeSvg(spotifyUrl),
            fetchTrackInfo(spotifyUrl)
        ]);

        currentSpotifyCodeSvg = svgData;
        currentTrackInfo = trackData;

        displayPreview(trackData, svgData);
    } catch (error) {
        showError(error.message || 'Failed to process Spotify URL');
    } finally {
        setProcessingState(false);
    }
}

// Display functions
function displayPreview(trackInfo, svgData) {
    // Update track info title
    trackInfoTitle.textContent = `${trackInfo.type.charAt(0).toUpperCase() + trackInfo.type.slice(1)} Information`;
    
    // Render track info content
    trackInfoContent.innerHTML = renderTrackInfo(trackInfo);
    
    // Display Spotify Code SVG
    if (svgData) {
        spotifyCodeDisplay.innerHTML = svgData;
        spotifyCodeSection.classList.remove('hidden');
    }
    
    // Show preview section
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

// Purchase handler
async function handlePurchase() {
    if (!currentTrackInfo || !currentSpotifyCodeSvg) {
        showError('Please generate a keychain first');
        return;
    }

    try {
        // Send data to your FastAPI backend for payment processing
        const response = await fetch(`${API_BASE_URL}/api/create-payment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                track_info: currentTrackInfo,
                spotify_code_svg: currentSpotifyCodeSvg,
                spotify_url: spotifyUrlInput.value
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Redirect to payment URL (Stripe checkout) or handle payment flow
        if (data.payment_url) {
            window.location.href = data.payment_url;
        } else {
            alert('Payment processing initiated! Check your email for download instructions.');
        }
    } catch (error) {
        console.warn('Backend not available for payment processing:', error.message);
        alert('Payment processing is currently unavailable. Please try again later when the backend server is running.');
    }
}