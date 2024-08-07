package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"sync"
)

type FirstResponse struct {
	Result struct {
		ID string `json:"id"`
	} `json:"result"`
}

type SecondResponse struct {
	// Define the structure according to the second API response
}

func makeRequests(firstApiUrl, secondApiUrl string, firstRequestData map[string]interface{}, wg *sync.WaitGroup, results chan<- string, errs chan<- error) {
	defer wg.Done()

	client := &http.Client{}

	// Make the first API request
	firstRequestBody, _ := json.Marshal(firstRequestData)
	req, err := http.NewRequest("POST", firstApiUrl, bytes.NewBuffer(firstRequestBody))
	if err != nil {
		errs <- err
		return
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		errs <- err
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		errs <- fmt.Errorf("first API request failed with status code: %d", resp.StatusCode)
		return
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		errs <- err
		return
	}
    fmt.Println("Here the first response", string(body))
	var firstResponse FirstResponse
	if err := json.Unmarshal(body, &firstResponse); err != nil {
		errs <- err
		return
	}

	id := firstResponse.Result.ID
	fmt.Println("id:", id)

	// Prepare the second request data using the response from the first request
	secondRequestData := map[string]interface{}{
		"id":       id,
		"password": "mypassword",
	}

	// Make the second API request
	secondRequestBody, _ := json.Marshal(secondRequestData)
	req, err = http.NewRequest("POST", secondApiUrl, bytes.NewBuffer(secondRequestBody))
	if err != nil {
		errs <- err
		return
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	if err != nil {
		errs <- err
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		errs <- fmt.Errorf("second API request failed with status code: %d", resp.StatusCode)
		return
	}

	body, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		errs <- err
		return
	}

	var secondResponse SecondResponse
	if err := json.Unmarshal(body, &secondResponse); err != nil {
		errs <- err
		return
	}

	// Handle the response from the second API request
	results <- fmt.Sprintf("Second API Response: %s", string(body))
}

func loadRequestData() ([]map[string]interface{}, error) {
	file, err := os.Open("reqs.json")
    if err != nil {
        return nil, err
    }
    defer file.Close()

    // Read the file content
    byteValue, err := ioutil.ReadAll(file)
    if err != nil {
        return nil, err
    }

    // Unmarshal the JSON content into a slice of Person
    var requestsMap []map[string]interface{}
    err = json.Unmarshal(byteValue, &requestsMap)
    if err != nil {
        return nil, err
    }

    return requestsMap, nil
}

func main() {
	firstApiUrl := "http://localhost:20009/api/initiate-rbt-transfer"
	secondApiUrl := "http://localhost:20009/api/signature-response"
	requestDataList, err := loadRequestData()
	if err != nil {
		panic(err)
	}

	var wg sync.WaitGroup
	results := make(chan string, len(requestDataList))
	errs := make(chan error, len(requestDataList))

	for x, requestData := range requestDataList {
		wg.Add(1)
		fmt.Printf("Sent Request: %v", x)
		go makeRequests(firstApiUrl, secondApiUrl, requestData, &wg, results, errs)
	}

	wg.Wait()
	close(results)
	close(errs)

	for result := range results {
		fmt.Println(result)
	}

	for err := range errs {
		if err != nil {
			log.Println("Error:", err)
		}
	}
}
