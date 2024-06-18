from flask import Flask, request, jsonify, render_template
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)


plt.switch_backend('Agg')

class DiskScheduler:
    def __init__(self, initial_position, requests):
        self.initial_position = initial_position
        self.requests = list(map(int, requests))  # Convert requests to integers

    def fcfs(self):
        total_movement = 0
        current_position = self.initial_position
        sequence = [current_position]

        for request in self.requests:
            total_movement += abs(request - current_position)
            current_position = request
            sequence.append(current_position)

        return total_movement, sequence

    def sstf(self):
        total_movement = 0
        current_position = self.initial_position
        sequence = [current_position]
        requests = self.requests[:]

        while requests:
            closest_request = min(requests, key=lambda x: abs(x - current_position))
            total_movement += abs(closest_request - current_position)
            current_position = closest_request
            sequence.append(current_position)
            requests.remove(closest_request)

        return total_movement, sequence

    def scan(self):
        total_movement = 0
        current_position = self.initial_position
        sequence = [current_position]
        requests = sorted(self.requests)
        direction = 1  # 1 for up, -1 for down

        while requests:
            if direction == 1:
                for request in requests:
                    if request >= current_position:
                        total_movement += abs(request - current_position)
                        current_position = request
                        sequence.append(current_position)
                direction = -1
            else:
                for request in reversed(requests):
                    if request <= current_position:
                        total_movement += abs(request - current_position)
                        current_position = request
                        sequence.append(current_position)
                direction = 1
            requests = [r for r in requests if r not in sequence]

        return total_movement, sequence

    def c_scan(self):
        total_movement = 0
        current_position = self.initial_position
        sequence = [current_position]
        requests = sorted(self.requests)

        for request in requests:
            if request >= current_position:
                total_movement += abs(request - current_position)
                current_position = request
                sequence.append(current_position)

        if requests and current_position != max(requests):
            total_movement += abs(max(requests) - current_position)
            current_position = max(requests)
            sequence.append(current_position)

        total_movement += max(requests) - min(requests)
        current_position = min(requests)
        sequence.append(current_position)

        for request in requests:
            if request < self.initial_position:
                total_movement += abs(request - current_position)
                current_position = request
                sequence.append(current_position)

        return total_movement, sequence

    def look(self):
        total_movement = 0
        current_position = self.initial_position
        sequence = [current_position]
        requests = sorted(self.requests)
        direction = 1

        while requests:
            if direction == 1:
                for request in requests:
                    if request >= current_position:
                        total_movement += abs(request - current_position)
                        current_position = request
                        sequence.append(current_position)
                direction = -1
            else:
                for request in reversed(requests):
                    if request <= current_position:
                        total_movement += abs(request - current_position)
                        current_position = request
                        sequence.append(current_position)
                direction = 1
            requests = [r for r in requests if r not in sequence]

        return total_movement, sequence

    def c_look(self):
        total_movement = 0
        current_position = self.initial_position
        sequence = [current_position]
        requests = sorted(self.requests)

        for request in requests:
            if request >= current_position:
                total_movement += abs(request - current_position)
                current_position = request
                sequence.append(current_position)

        total_movement += abs(max(requests) - min(requests))
        current_position = min(requests)
        sequence.append(current_position)

        for request in requests:
            if request < self.initial_position:
                total_movement += abs(request - current_position)
                current_position = request
                sequence.append(current_position)

        return total_movement, sequence

def generate_graph(sequence, title):
    plt.figure(figsize=(8, 5))
    plt.plot(sequence, marker='o')
    plt.title(title)
    plt.xlabel('Steps')
    plt.ylabel('Cylinder')
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.read()).decode('utf-8')
    plt.close()  # Close the plot to release resources

    return img_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<algorithm>', methods=['POST'])
def schedule(algorithm):
    data = request.get_json()
    initial_position = int(data['initial_position'])  # Convert to integer
    requests = data['requests']

    scheduler = DiskScheduler(initial_position, requests)
    if algorithm == 'fcfs':
        total_movement, sequence = scheduler.fcfs()
    elif algorithm == 'sstf':
        total_movement, sequence = scheduler.sstf()
    elif algorithm == 'scan':
        total_movement, sequence = scheduler.scan()
    elif algorithm == 'c_scan':
        total_movement, sequence = scheduler.c_scan()
    elif algorithm == 'look':
        total_movement, sequence = scheduler.look()
    elif algorithm == 'c_look':
        total_movement, sequence = scheduler.c_look()
    else:
        return jsonify({"error": "Invalid algorithm"}), 400

    img_base64 = generate_graph(sequence, algorithm.upper() + ' Disk Scheduling')

    response = {
        'total_head_movement': total_movement,
        'sequence_of_access': sequence,
        'graph': img_base64
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
