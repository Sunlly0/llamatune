# import logging
import grpc
# pylint: disable=import-error
from executors.grpc.nautilus_rpc_pb2 import ExecuteRequest, EmptyMessage
from executors.grpc.nautilus_rpc_pb2_grpc import ExecutionServiceStub
from executors.executor import ExecutorInterface

class NautilusExecutor(ExecutorInterface):
    GRPC_MAX_MESSAGE_LENGTH = 32 * (2 ** 20) # 32MB
    # NOTE: Nautilus already has a soft time limit (default is *1.5 hour*)
    EXECUTE_TIMEOUT_SECS = 2 * 60 * 60 # 4 hours

    def __init__(self,  host=None, port=None, n_retries=10,spaces=None, storage=None):
        super().__init__(spaces, storage)
        
        self.spaces = None
        self.storage = None
        self.host, self.port = host, port
        self.iter = 0

        delay = 2
        for idx in range(1, n_retries + 1):
            print(f'Trying connecting to Nautilus [#={idx}]...')
            try:
                self._try_connect(timeout=5)
            except Exception as err:
                print(f'Failed to connect: {repr(err)}')
                print(f'Trying again in {delay} seconds')
                # time.sleep(delay)
                delay *= 2
            else:
                print('Connected to Nautilus!')
                return

        raise RuntimeError(f'Cannot connect to Nautilus @ {host}:{port}')
    
    def _try_connect(self, **kwargs):
        """ Attempt to connect to host:port address """
        self.channel = grpc.insecure_channel(
            f'{self.host}:{self.port}',
            options=[ # send/recv up to 32 MB of messages (4MB default)
                ('grpc.max_send_message_length', self.GRPC_MAX_MESSAGE_LENGTH),
                ('grpc.max_receive_message_length', self.GRPC_MAX_MESSAGE_LENGTH),
            ])
        self.stub = ExecutionServiceStub(self.channel)
        ## 此处报错 时间戳的类型不对
        response = self.stub.Heartbeat(EmptyMessage(), **kwargs)
        print(f'{10*"="} Nautilus Info {10*"="}')
        print(f'Alive since  : {response.alive_since.ToDatetime()}')
        print(f'Current time : {response.time_now.ToDatetime()}')
        print(f'Jobs finished: {response.jobs_finished}')
        # logger.info(f'{35 * "="}')
        
    def evaluate_configuration(self, dbms_info, benchmark_info):
        print("")
        
    
def run():
     executor=NautilusExecutor(host="172.20.0.2",port="50051")
     
    
if __name__ == '__main__':
    run()