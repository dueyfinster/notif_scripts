#!/bin/bash
CONTAINER=postgres
USER=pguser

backup(){
    docker exec -t "$CONTAINER" pg_dumpall -c -U "$USER" > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
}

restore(){
    cat *.sql | docker exec -i "$CONTAINER" psql -U "$USER"
}

backup()