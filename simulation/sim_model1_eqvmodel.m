clear all; close all; clc;
% Codes for ECS289F - "Opinion dynamics w/ reluctant agents"
% Feel free to play around with it...

N = 10;
A = ones(N) - eye(N); % This is a fully connected graph
iter_max = 5e2; % the max. no. of iterations 

flag = 0; % if flag = 0, run the standard reluctant agent model -> results in biased average
% if flag = 1, then the agents will "delay" until making the next update.
% In this case, the reluctant model will find the true average.

% Specify the adaptivity of the agents
tau_x = ones(N,1); 
tau_x([1 2]) = 3; % select the reluctant agents

the_vector = zeros(N,500);

for monte_carlo = 1 : 500
x0 = 10*rand(N,1); % Initialize the opinion with some random numbers..
x_avg = mean(x0); 

% Init. the algorithms
x_gossip = x0; x_model1 = x0; xh_model1 = x0; xo_model1 = x0;

x_augmented = zeros(N-2 + 4 + (3-1)*2*2,1); x_augmented(1:N) = x0; 
% only deal with the 2 reluctant agents w/ tau = 3 case

A_const = zeros(8,length(x_augmented)); % this matrix account for the delays
A_const(1,1) = 1; A_const(2,N+3) = 1; A_const(3,N+1) = 1; A_const(4,N+5) = 1; 
A_const(5,2) = 1; A_const(6,N+7) = 1; A_const(7,N+2) = 1; A_const(8,N+9) = 1;

A_accum = zeros(length(x_augmented),length(x_augmented),2*iter_max);
cnt_anal = 100*ones(N,1);

cnt_xh = ones(N,1);
sq_dist_gos = zeros(iter_max,1); sq_dist_model1 = sq_dist_gos;

for iter_no = 1 : iter_max
    % A random node wake up at this time
    src_node = randint(1,1,[1 N]);
    % It selects a random neighbor with uniform probability
    pos_set = [1:src_node-1 src_node+1:N];
    pos_choice = find(A(src_node,pos_set)>0);
    dst_node_idx = randint(1,1,[1 length(pos_choice)]);
    dst_node = pos_set(dst_node_idx);
    
    % Baseline: the two nodes communicates and update opinions instantly
    tmp_avg = (x_gossip(src_node) + x_gossip(dst_node))/2;
    x_gossip(src_node) = tmp_avg;
    x_gossip(dst_node) = tmp_avg;
    
    % For benchmarking: evaluate the square distance
    sq_dist_gos(iter_no) = sqrt(sum( (x_gossip-x_avg).^2 ));
    
    % Model 1 with reluctant agent
    cnt_xh = cnt_xh + 1;
    cnt_xh = min( tau_x, cnt_xh ); % such that the counter is bounded
    
    if ( (mod(iter_no,10) == 0) || (flag == 0) )
        cnt_xh(src_node) = 1; cnt_xh(dst_node) = 1; % reset the counters
        xo_model1(src_node) = x_model1(src_node); xo_model1(dst_node) = x_model1(dst_node);
        % tmp_avg is the average of the two agents' opinion
        tmp_avg = (x_model1(src_node) + x_model1(dst_node))/2;
        % xh_model1 corresponds to the \hat{x} in the writeup
        xh_model1(src_node) = tmp_avg; xh_model1(dst_node) = tmp_avg;
    end
    % we now evaluate the updates for both agents according to the
    % designed rule
    for n = 1 : N
        x_model1(n) = (cnt_xh(n)/tau_x(n))*xh_model1(n) + ...
            ((tau_x(n)-cnt_xh(n))/tau_x(n))*xo_model1(n);
    end
    % eval. the squared distance now
    sq_dist_model1(iter_no) = sqrt(sum( (x_model1-x_avg).^2 ));
    
    % Testing the model against the augmented system, as inspired by
    % Angelia's 2007 paper. 
    % To Chris: please don't code the following into your C/python program
    % My intention here is only to analyze the dynamics.
    
    % Basically I only want to construct A
    % 1st stage the "update" stage
    A_current = eye(length(x_augmented)); A_current(N+3:end,:) = A_const;
    if src_node <= 2
        % we need some special treatment about this case
        A_current(src_node+N,src_node+N) = 0;
        A_current(src_node+N,src_node) = 0.5; A_current(src_node+N,dst_node) = 0.5; % for x_hat
    else
        % the src_node is normal
        A_current(src_node,src_node) = 0.5; A_current(src_node,dst_node) = 0.5;
    end
    if dst_node <= 2
        % we need some special treatment about this case
        A_current(dst_node+N,dst_node+N) = 0;
        A_current(dst_node+N,dst_node) = 0.5; A_current(dst_node+N,src_node) = 0.5; % for x_hat
    else
        A_current(dst_node,dst_node) = 0.5; A_current(dst_node,src_node) = 0.5;
    end
    A_accum(:,:,2*iter_no-1) = A_current;
    
    x_augmented = A_current*x_augmented;
    
    % 2nd stage the adaptation stage...
    A_current = eye(length(x_augmented));
    % Its construction depends on the counter variable... --> we have two
    % counter to check...
    cnt_anal = cnt_anal + 1;
    cnt_anal(src_node) = 1; cnt_anal(dst_node) = 1;
    if cnt_anal(1) == 1
        A_current(1,1) = 0;
        A_current(1,N+1) = 1/3; A_current(1,N+2+(1-1)*4+1) = 2/3;
    elseif cnt_anal(1) == 2
        A_current(1,1) = 0;
        A_current(1,N+2+(1-1)*4+3) = 2/3;
        A_current(1,N+2+(1-1)*4+2) = 1/3;
    elseif cnt_anal(1) == 3
        A_current(1,1) = 0;
        A_current(1,N+2+(1-1)*4+4) = 1;
    end
    
    if cnt_anal(2) == 1
        A_current(2,2) = 0;
        A_current(2,N+2) = 1/3; A_current(2,N+2+(2-1)*4+1) = 2/3;
    elseif cnt_anal(2) == 2
        A_current(2,2) = 0;
        A_current(2,N+2+(2-1)*4+3) = 2/3;
        A_current(2,N+2+(2-1)*4+2) = 1/3;
    elseif cnt_anal(2) == 3
        A_current(2,2) = 0;
        A_current(2,N+2+(2-1)*4+4) = 1;
    end
    A_accum(:,:,2*iter_no) = A_current;
    
    x_augmented = A_current*x_augmented;

end

% fprintf('Sq. Dist to true average (baseline): %f ||',sq_dist_gos(end));
% fprintf('Sq. Dist to true average (Model1): %f \n',sq_dist_model1(end));
% 
% semilogy(1:iter_max,sq_dist_gos,1:iter_max,sq_dist_model1)

% Let me calculate the A^\infty
A_recursive = A_accum(:,:,1);
for iii = 2 : 2*iter_max
    A_recursive = A_accum(:,:,iii)*A_recursive;
end

the_vector(:,monte_carlo) = A_recursive(1,1:N);


% recip = [0.8587 0.8507 1.0479 1.0498 1.0365 1.0513 1.0354 1.0449 1.0527 1.0372];
recip = 0.1 ./ the_vector(:,monte_carlo)';
x_corrected = mean( recip.* x_model1' );


end