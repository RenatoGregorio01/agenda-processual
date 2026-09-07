package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"
)

type job struct {
	ID         string `json:"id"`
	NumeroOab  string `json:"numero_oab"`
	UfOab      string `json:"uf_oab"`
	DataInicio string `json:"data_inicio"`
	DataFim    string `json:"data_fim"`
}

func main() {
	api, token := os.Getenv("INTERNAL_API_URL"), os.Getenv("INTEGRATION_WORKER_TOKEN")
	if api == "" || len(token) < 32 {
		log.Fatal("INTERNAL_API_URL e INTEGRATION_WORKER_TOKEN (32+ caracteres) são obrigatórios")
	}
	client := &http.Client{Timeout: 30 * time.Second}
	for {
		if err := run(context.Background(), client, api, token); err != nil {
			log.Printf("worker: %v", err)
		}
		time.Sleep(10 * time.Second)
	}
}

func run(ctx context.Context, c *http.Client, api, token string) error {
	jobs := []job{}
	if err := call(ctx, c, http.MethodPost, api+"/api/v1/djen/internal/jobs/claim", token, nil, &jobs); err != nil {
		return err
	}
	for _, j := range jobs {
		u, _ := url.Parse("https://comunicaapi.pje.jus.br/api/v1/comunicacao")
		q := u.Query()
		q.Set("numeroOab", j.NumeroOab)
		q.Set("ufOab", j.UfOab)
		q.Set("dataDisponibilizacaoInicio", j.DataInicio)
		q.Set("dataDisponibilizacaoFim", j.DataFim)
		q.Set("pagina", "1")
		q.Set("itensPorPagina", "50")
		u.RawQuery = q.Encode()
		var result struct {
			Items []map[string]any `json:"items"`
		}
		err := call(ctx, c, http.MethodGet, u.String(), "", nil, &result)
		path := fmt.Sprintf("%s/api/v1/djen/internal/jobs/%s/", api, j.ID)
		if err != nil {
			_ = call(ctx, c, http.MethodPost, path+"fail", token, map[string]string{"mensagem": err.Error()}, nil)
			continue
		}
		if err = call(ctx, c, http.MethodPost, path+"complete", token, map[string]any{"items": result.Items}, nil); err != nil {
			return err
		}
	}
	return nil
}

func call(ctx context.Context, c *http.Client, method, uri, token string, body, out any) error {
	var r *bytes.Reader
	if body != nil {
		b, e := json.Marshal(body)
		if e != nil {
			return e
		}
		r = bytes.NewReader(b)
	} else {
		r = bytes.NewReader(nil)
	}
	req, e := http.NewRequestWithContext(ctx, method, uri, r)
	if e != nil {
		return e
	}
	if token != "" {
		req.Header.Set("X-Integration-Worker-Token", token)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	res, e := c.Do(req)
	if e != nil {
		return e
	}
	defer res.Body.Close()
	if res.StatusCode/100 != 2 {
		return fmt.Errorf("HTTP %s", res.Status)
	}
	if out != nil {
		return json.NewDecoder(res.Body).Decode(out)
	}
	return nil
}
