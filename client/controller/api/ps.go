package api

import "github.com/deis/pkg/time"

// Pods defines the structure of a process.
type Pods struct {
	Release string    `json:"release"`
	Type    string    `json:"type"`
	Name    string    `json:"name"`
	State   string    `json:"state"`
	Started time.Time `json:"started"`
}
