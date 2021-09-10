if __name__ == '__main__':
    import uvicorn
    uvicorn.run('demo.app:app', debug=True, port=5000)
