from flask import Flask, render_template, request, send_file, jsonify
from pytube import YouTube, Playlist
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create downloads directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        url = data.get('url')
        download_type = data.get('type')

        if not url or not download_type:
            return jsonify({
                'success': False,
                'error': 'URL and type are required'
            }), 400

        if download_type == 'video':
            try:
                yt = YouTube(url)
                video = yt.streams.get_highest_resolution()
                # Sanitize filename
                filename = "".join(x for x in yt.title if x.isalnum() or x in (' ', '-', '_')).rstrip() + '.mp4'
                filepath = os.path.join('downloads', filename)
                video.download('downloads', filename=filename)
                logger.info(f'Successfully downloaded video: {filename}')
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'title': yt.title,
                    'thumbnail': yt.thumbnail_url
                })
            except Exception as e:
                logger.error(f'Error downloading video: {str(e)}')
                return jsonify({
                    'success': False,
                    'error': f'Error downloading video: {str(e)}'
                }), 400

        elif download_type == 'playlist':
            try:
                playlist = Playlist(url)
                # Sanitize playlist title
                playlist_title = "".join(x for x in playlist.title if x.isalnum() or x in (' ', '-', '_')).rstrip()
                playlist_dir = os.path.join('downloads', playlist_title)

                if not os.path.exists(playlist_dir):
                    os.makedirs(playlist_dir)

                videos = []
                for video in playlist.videos:
                    try:
                        video_stream = video.streams.get_highest_resolution()
                        filename = "".join(x for x in video.title if x.isalnum() or x in (' ', '-', '_')).rstrip() + '.mp4'
                        video_stream.download(playlist_dir, filename=filename)
                        videos.append({
                            'title': video.title,
                            'thumbnail': video.thumbnail_url
                        })
                        logger.info(f'Successfully downloaded playlist video: {filename}')
                    except Exception as e:
                        logger.error(f'Error downloading video {video.title}: {str(e)}')
                        continue

                return jsonify({
                    'success': True,
                    'playlist_title': playlist_title,
                    'videos': videos
                })
            except Exception as e:
                logger.error(f'Error downloading playlist: {str(e)}')
                return jsonify({
                    'success': False,
                    'error': f'Error downloading playlist: {str(e)}'
                }), 400

        else:
            return jsonify({
                'success': False,
                'error': 'Invalid download type'
            }), 400

    except Exception as e:
        logger.error(f'Error during download: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/downloads/<path:filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join('downloads', filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f'Error downloading file {filename}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 