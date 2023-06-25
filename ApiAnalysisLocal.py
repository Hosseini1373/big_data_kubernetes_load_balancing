''''
This is a Python script that performs a load test on a local API server. 
The purpose is to send multiple simultaneous requests to the server and measure 
its performance under stress. The script logs the number of successful responses, 
timeouts, average response time, and total time taken for each set of concurrent requests. 
The results are stored in CSV files and visualized using various types of plots. Here's a
 more detailed explanation:
Overall, the script is a good example of how to run a simple load test on an API and visualize the results.
'''


''''
**Libraries**: The script uses multiple libraries such as `requests` to send HTTP requests, 
`multiprocessing` for parallel processing, `matplotlib` for data visualization, `pandas` for 
data handling, `csv` to write results into CSV files, and `os` for operating system dependent functionality.

'''
from multiprocessing import Process, Queue
import time
import requests
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import csv 
import time
import pandas as pd
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




'''
The `create_boxplots` function**: This function reads the CSV file of results, 
and generates four boxplots for Success Count, Timeout Count, Average Response 
Time, and Total Time Taken.
'''
def create_boxplots(filename):
    # Read the data from the CSV file
    data = pd.read_csv(filename)

    # Create a new figure with 4 subplots
    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(20, 5))  # Adjust the figure size if necessary

    # Create boxplots
    ax[0].boxplot(data['Success_Count'], vert=False)
    ax[0].set_title('Success Count')

    ax[1].boxplot(data['Timeout_Count'], vert=False)
    ax[1].set_title('Timeout Count')

    ax[2].boxplot(data['Average_Response_Time'], vert=False)
    ax[2].set_title('Average Response Time')

    ax[3].boxplot(data['Total_Time_Taken'], vert=False)  # New boxplot for total time taken
    ax[3].set_title('Total Time Taken')

    # Save the figure
    plt.savefig(filename.replace('.csv', '.png'))



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
def visualize_results(success_count, timeout_count, average_response_time, success_response_times, conc,iteration):
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
        plt.savefig(f'images/local/api_test_results_{iteration}_{conc}.png')
        figures.append(fig1.number)

        # Histogram for response time distribution
        fig2 = plt.figure()
        plt.hist(success_response_times, bins=20, edgecolor='black')
        plt.xlabel('Response Time (s)')
        plt.ylabel('Count')
        plt.title('Response Time Distribution of successful queries')
        plt.savefig(f'images/local/response_time_distribution_{iteration}_{conc}.png')
        figures.append(fig2.number)

        # Box plot for response times
        fig3 = plt.figure()
        plt.boxplot(success_response_times, vert=False)
        plt.xlabel('Response Time (s)')
        plt.yticks([])
        plt.title('Response Time of successful queries')
        plt.savefig(f'images/local/response_time_box_plot_{iteration}_{conc}.png')
        figures.append(fig3.number)

        # Response time percentiles
        fig4 = plt.figure()
        percentiles = [50, 90, 95, 99]
        perc_values = np.percentile(success_response_times, percentiles)
        plt.bar([f"{p}th" for p in percentiles], perc_values)
        plt.xlabel('Percentile')
        plt.ylabel('Response Time (s)')
        plt.title('Response Time Percentiles of successful queries')
        plt.savefig(f'images/local/response_time_percentiles_{iteration}_{conc}.png')
        figures.append(fig4.number)

        #create_buttons() #we don't want to plot anything and just save the images

    else:
        print("No successful requests to display graphs.")




''''
The `if __name__ == '__main__':` block**: This is the main driver of the script. 
It runs the load test with two different levels of concurrency, 4 and 8. For 
each level, it sends simultaneous requests 10 times. It starts multiple processes,
 each sending a request, and waits for all to finish. The results are gathered 
 from the multiprocessing Queue, and then analyzed to calculate the number of 
 successes, timeouts, the average response time, and the total time taken. These 
 results are visualized and saved to a CSV file. Finally, the CSV file is used 
 to create boxplots.
'''
if __name__ == '__main__':
    for conc in [4,8]:
        all_results = []
        for iteration in range(10):  # Total 9 times = 1 + 8 more times
            print(f"---- Starting experiment {iteration + 1} ----")
            start = time.time()
            procs = []
            results_queue = Queue()
            for i in range(0, conc):
                proc = Process(target=requesting, args=(results_queue,))
                procs.append(proc)
                proc.start()

            results = []
            for proc in procs:
                proc.join()
                if not results_queue.empty():
                    results.append(results_queue.get())

            success_count = sum(1 for result in results if result[0] == 'success')
            timeout_count = sum(1 for result in results if result[0] == 'timeout')
            success_response_times = [result[1] for result in results if result[0] == 'success']
            average_response_time = np.mean(success_response_times)
            total_time_taken = time.time() - start
            print(f"Total time taken: {total_time_taken:.2f} seconds")
            print(f"Success count: {success_count}")
            print(f"Timeout count: {timeout_count}")
            print(f"Average response time: {average_response_time:.2f} seconds")
            all_results.append([success_count, timeout_count, average_response_time, total_time_taken])
            # Write results to a CSV file
            visualize_results(success_count, timeout_count, average_response_time, success_response_times, conc,iteration)

        # Write results to a CSV file
        with open(f'images/local/results_{conc}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Success_Count', 'Timeout_Count', 'Average_Response_Time', 'Total_Time_Taken'])  # Update the header
            writer.writerows(all_results)  # Write data rows

        # Create and save boxplots
        create_boxplots(f'images/local/results_{conc}.csv')




