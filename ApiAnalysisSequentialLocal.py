'''
This Python script is designed to test the performance of a specific API endpoint. 
It performs the following tasks:

1. Makes 10 requests to the API endpoint `http://192.168.1.8:5000/query?query=Who%20is%20John` 
with a timeout of 200 seconds each.

2. It uses a technique called exponential backoff to handle cases where the request fails for any reason, 
including receiving a non-200 status code or an exception being thrown. This technique involves waiting 
for a certain period of time before making another attempt. The wait time is initially 1 second but 
doubles after each failed attempt, up to a maximum of the initial timeout value.

3. The results of each request, including the outcome (success or timeout) and the time taken, are 
placed into a multiprocessing Queue.

4. Once all the requests have been made, it processes the results, calculating the number of successful
 and timed-out requests, the average response time for successful requests, and the individual response times.

5. Finally, it visualizes the results using matplotlib, generating four different plots:

   - A bar chart showing the number of successful and timed-out requests
   - A histogram showing the distribution of response times for successful requests
   - A box plot also showing the distribution of response times for successful requests
   - A bar chart showing certain percentiles (50th, 90th, 95th, and 99th) of the response times 
   for successful requests

6. These plots are then saved as images in a directory named 'images/K8/'.

The code also includes some unused functionality for navigating between the different 
plots using 'Next' and 'Back' buttons. This functionality would be useful if you wanted to 
\display the plots interactively rather than saving them as images.

However, note that all requests are made in a single process in the main function. This is 
generally less efficient than using multiple processes or threads, especially for IO-bound tasks 
like making HTTP requests. If you wanted to make the requests in parallel, you could create a separate 
Process for each one and then join them all before processing the results.
'''



''''
Importing libraries
'''
from multiprocessing import Process, Queue
import time
import requests
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import os



''''
The `requesting` function**: This function sends a GET request to a 
specific API endpoint and then puts the results in a multiprocessing Queue. 
If the request is successful (status code 200), it puts a tuple ('success', response_time) 
in the queue. If the request fails, it implements an exponential backoff strategy, i.e., 
the function waits for an increasing amount of time after each failed attempt before trying again. 
If a timeout occurs, it checks if there's still time left to retry, and if not, it reports it as a timeout. 
Other exceptions are handled in a similar manner.
'''
def requesting(results_queue):
    max_time = 200  # Maximum time to wait
    start_time = time.time()
    base_wait_time = 1  # Base wait time, adjust as needed
    attempts = 0  # Number of attempts made

    while True:
        try:
            response = requests.get('http://192.168.1.8:5000/query?query=Who%20is%20John', timeout=max_time)
            response_time = time.time() - start_time
            if response.status_code == 200:
                results_queue.put(('success', response_time))
                break
            else:
                # Instead of putting 'failure' into queue, we implement exponential backoff here
                wait_time = min(max_time, base_wait_time * 2 ** attempts)  # Exponential backoff, but not exceeding max_time
                time.sleep(wait_time)
                attempts += 1
        except requests.exceptions.Timeout as e:
            # If a timeout occurs, check if we still have time to retry
            elapsed_time = time.time() - start_time
            if elapsed_time < max_time:
                wait_time = min(max_time - elapsed_time, base_wait_time * 2 ** attempts)  # Exponential backoff, but not exceeding remaining time
                time.sleep(wait_time)
                attempts += 1
            else:
                # If no time is left, report it as a timeout
                results_queue.put(('timeout', elapsed_time, -1, str(e)))
                break
        except requests.exceptions.RequestException as e:
            # For any other exception, check if we have time to retry
            elapsed_time = time.time() - start_time
            if elapsed_time < max_time:
                wait_time = min(max_time - elapsed_time, base_wait_time * 2 ** attempts)  # Exponential backoff, but not exceeding remaining time
                time.sleep(wait_time)
                attempts += 1
            else:
                # If no time is left, report it as a timeout
                results_queue.put(('timeout', elapsed_time, -1, str(e)))
                break


''''
(not used)
The `on_next` and `on_back` functions**: These functions are used for navigating 
through the plots. They change the current plot shown based on button clicks.
'''
def on_next(event):
    global current_figure
    current_figure += 1
    current_figure %= len(figures)
    plt.figure(figures[current_figure])
    plt.show()

def on_back(event):
    global current_figure
    current_figure -= 1
    current_figure %= len(figures)
    plt.figure(figures[current_figure])
    plt.show()


''''
(not used)
The `create_buttons` function**: This function creates two buttons for 
navigating through the plots, 'Next' and 'Back'. The respective on_click 
events are attached to the buttons.
'''
def create_buttons():
    plt.figure()
    ax_back = plt.axes([0.3, 0.05, 0.1, 0.075])
    ax_next = plt.axes([0.7, 0.05, 0.1, 0.075])
    b_back = Button(ax_back, 'Back')
    b_next = Button(ax_next, 'Next')
    b_back.on_clicked(on_back)
    b_next.on_clicked(on_next)
    plt.show()



''''
The `visualize_results` function**: This function visualizes the results 
of the load test. It creates bar charts, histograms, box plots and percentile 
plots. The figures are then saved as png images.
'''
def visualize_results(success_count, timeout_count, average_response_time, success_response_times):
    global figures
    global current_figure
    figures = []
    current_figure = 0
    if not os.path.exists('images/local/'):
        os.makedirs('images/local/')
    if success_count > 0:
        # Bar chart for success,  and timeout counts
        fig1 = plt.figure()
        plt.bar(['Success', 'Timeout'], [success_count, timeout_count])
        plt.xlabel('Result')
        plt.ylabel('Count')
        plt.title('API Test Results')
        plt.savefig(f'images/local/api_test_results.png')
        figures.append(fig1.number)

        # Histogram for response time distribution
        fig2 = plt.figure()
        plt.hist(success_response_times, bins=20, edgecolor='black')
        plt.xlabel('Response Time (s)')
        plt.ylabel('Count')
        plt.title('Response Time Distribution of successful queries')
        plt.savefig(f'images/local/response_time_distribution.png')
        figures.append(fig2.number)

        # Box plot for response times
        fig3 = plt.figure()
        plt.boxplot(success_response_times, vert=False)
        plt.xlabel('Response Time (s)')
        plt.yticks([])
        plt.title('Response Time of successful queries')
        plt.savefig(f'images/local/response_time_box_plot.png')
        figures.append(fig3.number)

        # Response time percentiles
        fig4 = plt.figure()
        percentiles = [50, 90, 95, 99]
        perc_values = np.percentile(success_response_times, percentiles)
        plt.bar([f"{p}th" for p in percentiles], perc_values)
        plt.xlabel('Percentile')
        plt.ylabel('Response Time (s)')
        plt.title('Response Time Percentiles of successful queries')
        plt.savefig(f'images/local/response_time_percentiles.png')
        figures.append(fig4.number)

        #create_buttons()

    else:
        print("No successful requests to display graphs.")





''''
The main function in this script initiates a series of API requests, collects their results, 
and then generates a set of visualizations based on these results.
Specifically, it sends 10 requests to a predefined API endpoint. These requests are sent one 
after the other, not in parallel.
The results of each request, including the status (success or timeout) and the response time, 
are collected and stored in a queue for further processing.
After all requests have been made, the script counts the number of successful and timed-out 
requests, calculates the average response time for the successful ones, and then prints out these statistics.
Finally, the main function calls a visualization function to generate a series of plots 
based on these results, such as a bar chart of success and timeout counts, a histogram and a boxplot of response times, and a bar chart of response time percentiles. The generated plots are saved as image files in a predefined directory.
'''
if __name__ == '__main__':
    start = time.time()
    results_queue = Queue()
    
    for i in range(10):
        requesting(results_queue)

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

        success_count = sum(1 for result in results if result[0] == 'success')
        timeout_count = sum(1 for result in results if result[0] == 'timeout')
        success_response_times = [result[1] for result in results if result[0] == 'success']
        average_response_time = np.mean(success_response_times)

        print(f"Total time taken: {time.time() - start:.2f} seconds")
        print(f"Success count: {success_count}")
        print(f"Timeout count: {timeout_count}")
        print(f"Average response time: {average_response_time:.2f} seconds")




    visualize_results(success_count,  timeout_count, average_response_time, success_response_times)
